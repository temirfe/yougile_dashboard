from yougile.models import Ycolumn, Task
import logging
from yougile.services.yg_api_client import ExternalApiClient, ExternalApiException

logger = logging.getLogger(__name__)

def fetch_tasks(company, column_id=None, offset=0, limit=1000):
    """
    Fetches projects using the common API client.
    """
    try:
        api_client = ExternalApiClient(company=company)
        params={'limit':limit, 'offset':offset}
        if column_id:
            params['columnId']=column_id
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

def save_tasks(tasks):
    # Extract all unique column_ids
    unique_column_api_ids = set(bd.get('columnId') for bd in tasks if 'columnId' in bd)
    #logger.info(f"unique_column_api_ids {unique_column_api_ids}")

    # Fetch all necessary Ycolumn objects in one query~
    columns = Ycolumn.objects.filter(api_id__in=list(unique_column_api_ids))
    column_lookup = {column.api_id: column for column in columns}

    objects_to_save = []

    for data in tasks:
        name = data.get('title')
        column_api_id = data.get('columnId')
        task_api_id = data.get('id')
        color = data.get('color')

        column = column_lookup.get(column_api_id)

        if not column:
            print(f"Warning: column with API ID {column_api_id} not found for task '{name}'. Skipping task.")
            continue

        # Create a Board instance (it won't hit the DB yet)
        objects_to_save.append(
            Task(
                title=name,
                api_id=task_api_id,
                column=column,
                column_api_id=column_api_id,
                color=color
            )
        )

    # Perform bulk_create with update_conflicts for upsert
    if objects_to_save:
        # The 'fields' argument specifies which unique constraint to check for conflicts.
        # It must match a unique field or a UniqueConstraint.
        # If a conflict occurs on 'api_id', then the 'update_fields' will be applied.
        created_count = Task.objects.bulk_create(
            objects_to_save,
            update_conflicts=True,
            unique_fields=['api_id'], # The field(s) used to detect a conflict
            update_fields=['title', 'board','board_api_id','color'] # The fields to update if a conflict occurs
        )
        print(f"Successfully processed {len(objects_to_save)} columns (created/updated).")
        # Note: bulk_create with update_conflicts returns the number of objects created on some backends,
        # but for others (like PostgreSQL) it returns the number of *inserted* rows, not including updates.
        # So, it's harder to get exact counts of created vs. updated from the return value.

def fetch_and_save_taks(company, column_id=None):
    ret = []
    has_next=True
    offset=0
    yoba = 0
    limit=1000
    while has_next:
        print(f"offset: {offset}, yoba: {yoba}")
        if yoba > 3:
            has_next = False
        result = fetch_tasks(company,column_id,offset,limit)
        if result and 'content' in result:
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
    return ret

def fetch_and_save_all_companies_tasks():
    companies = ['dartlab','prosoft','product','pm']
    results =[]
    for company in companies:
        res = fetch_and_save_taks(company)
        results.append(res)
    return results
