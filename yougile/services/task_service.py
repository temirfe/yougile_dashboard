from yougile.models import Ycolumn, Task
import logging
from yougile.services.yg_api_client import ExternalApiClient, ExternalApiException
import datetime
from django.utils import timezone
from account.models import Profile
from django.contrib.auth import get_user_model
from typing import Optional
import time

logger = logging.getLogger(__name__)
current_company = None

def fetch_task(company, task_api_id):
    """
    Fetches projects using the common API client.
    """
    global current_company
    current_company = company
    try:
        api_client = ExternalApiClient(company=company)
        # Just specify the endpoint relative to the base URL
        data = api_client.get(f"/tasks/{task_api_id}")
        return data
    except ExternalApiException as e:
        logger.error(f"Failed to fetch task: {task_api_id} (Status: {e.status_code})")
        # Re-raise or handle as per your application's error strategy
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching columns: {e}")
        raise

def fetch_tasks(company, column_api_id=None, offset=0, limit=1000):
    """
    Fetches projects using the common API client.
    """
    global current_company
    current_company = company
    try:
        api_client = ExternalApiClient(company=company)
        params={'limit':limit, 'offset':offset}
        if column_api_id:
            params['columnId']=column_api_id
        # Just specify the endpoint relative to the base URL
        data = api_client.get("/task-list", params=params)
        return data
    except ExternalApiException as e:
        logger.error(f"Failed to fetch columns: {e.message} (Status: {e.status_code})")
        # Re-raise or handle as per your application's error strategy
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching columns: {e}")
        raise

def save_tasks(tasks: list, parent: Optional[Task] = None):
    column_lookup={}
    if not parent:
        # Extract all unique column_ids
        unique_column_api_ids = set(bd.get('columnId') for bd in tasks if 'columnId' in bd)
        #logger.info(f"unique_column_api_ids {unique_column_api_ids}")

        # Fetch all necessary Ycolumn objects in one query~
        columns = Ycolumn.objects.filter(api_id__in=list(unique_column_api_ids))
        column_lookup = {column.api_id: column for column in columns}

    for data in tasks:
        save_single_task(data, column_lookup,parent)

def save_single_task(data: dict, column_lookup: dict, parent: Optional[Task] = None):
    if parent:
        column_api_id = parent.column_api_id
        column = parent.ycolumn
    else:
        column_api_id = data.get('columnId')
        column = column_lookup.get(column_api_id)
    tzone=timezone.get_current_timezone()
    timestamp = int(str(data['timestamp'])[:10])
    created_at = datetime.datetime.fromtimestamp(timestamp, tz=tzone)

    if not column:
        #print(f"Warning: column with API ID {column_api_id} not found for task. Skipping task.")
        #continue
        return
    to_save_map = {
        'title': data.get('title')[:250],
        'api_id':data.get('id'),
        'ycolumn':column, 
        'column_api_id':column_api_id,
        'created_at':created_at,
        'archived':data.get('archived',False),
        'completed':data.get('completed',False),
        'api_user_id':data.get('createdBy',''),
        'parent':parent
    }
    if 'completedTimestamp' in data:
        # Take the first 10 digits as string, convert to int timestamp
        ts_str = str(data['completedTimestamp'])[:10]
        ts_int = int(ts_str)
        to_save_map['completed_at'] = datetime.datetime.fromtimestamp(ts_int, tz=tzone)

    if 'description' in data:
        to_save_map['description']=data['description']

    if 'timeTracking' in data:
        if 'plan' in data['timeTracking']:
            to_save_map['time_plan']=data['timeTracking']['plan']
        if 'work' in data['timeTracking']:
            to_save_map['time_work']=data['timeTracking']['work']

    if 'deadline' in data:
        deadline=int(str(data['deadline']['deadline'])[:10])
        to_save_map['deadline']=datetime.datetime.fromtimestamp(deadline, tz=tzone)

    task, created = Task.objects.update_or_create(
            api_id=data['id'],
            defaults=to_save_map
        )
    """ if created:
        print(f'created {task.title}')
    else:
        print(f'updated {task.title}, id: {task.id}') """
    
    #check if task has users
    if 'assigned' in data:
        if isinstance(data['assigned'], list):
            user_ids = data['assigned']
        elif isinstance(data['assigned'], str):
            user_ids = [data['assigned']]
        User = get_user_model()
        users_to_add = User.objects.filter(profile__yougile_id__in=user_ids)
        task.users.add(*users_to_add)
    
    #check if task has subtasks
    if 'subtasks' in data:
        for task_id in data['subtasks']:
            result = fetch_task(current_company,task_id)
            print(f'subtask: {result['id']}')
            save_tasks([result], task)


def fetch_and_save_tasks(company, column_id=None):
    ret = []
    has_next=True
    offset=1350
    yoba = 0
    limit=25
    while has_next:
        print(f"offset: {offset}, yoba: {yoba}")
        if yoba > 1:
            has_next = False
        result = fetch_tasks(company,column_id,offset,limit)
        if result and 'content' in result:
            print(f'fetch_tasks result count: {len(result['content'])}')
            save_tasks(result['content'])
            ret.append(True)
            paging = result.get("paging", {})
            if paging.get("next"):
                offset += limit 
            else:
                has_next = False
        else:
            has_next = False
        yoba += 1
        print('sleeping...')
        time.sleep(20)
    return ret

def fetch_and_save_all_companies_tasks():
    exlude_columns = ['Testing Done','Done','Sprint Done','Test Complete','Test Completed', 'Done this week','Done for Today']
    
    companies = ['dartlab']
    #companies = ['dartlab','prosoft','product','pm']
    results =[]
    for company in companies:
        res = fetch_and_save_tasks(company)
        results.append(res)
    return results

def fetch_and_save_by_active_columns(start=70, increment=5):
    ret = []
    while end <= 303:
        end = start + increment
        i = start
        not_done_columns = Ycolumn.objects.not_dones()[start:end] #302
        for column in not_done_columns:
            print(f'i: {i}, start {start}, end {end}')
            company=column.board.project.company
            
            result = fetch_tasks(company,column.api_id)
            if result and 'content' in result:
                save_tasks(result['content'])
            else:
                print('suka')
            i+=1
        start +=increment
        time.sleep(30)
    return 'done'

def yoba():
    print('suka')