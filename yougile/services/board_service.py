from yougile.models import Project, Board
import logging
from yougile.services.yg_api_client import ExternalApiClient, ExternalApiException


logger = logging.getLogger(__name__)

def fetch_boards(company, project_id=''):
    """
    Fetches projects using the common API client.
    """
    try:
        api_client = ExternalApiClient(company=company)
        path="/boards"
        if project_id:
            path+=f"&projectId={project_id}"
        # Just specify the endpoint relative to the base URL
        api_data = api_client.get(path)
        return api_data
    except ExternalApiException as e:
        logger.error(f"Failed to fetch projects: {e.message} (Status: {e.status_code})")
        # Re-raise or handle as per your application's error strategy
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching projects: {e}")
        raise

def save_boards(boards):
    # Extract all unique project_ids
    unique_project_api_ids = set(bd.get('projectId') for bd in boards if 'projectId' in bd)

    # Fetch all necessary Project objects in one query
    projects = Project.objects.filter(api_id__in=list(unique_project_api_ids))
    project_lookup = {project.api_id: project for project in projects}

    board_objects_to_save = []

    for board_data in boards:
        board_name = board_data.get('title')
        project_api_id = board_data.get('projectId')
        board_api_id = board_data.get('id')

        project = project_lookup.get(project_api_id)

        if not project:
            print(f"Warning: Project with API ID {project_api_id} not found for board '{board_name}'. Skipping board.")
            continue

        # Create a Board instance (it won't hit the DB yet)
        board_objects_to_save.append(
            Board(
                title=board_name,
                api_id=board_api_id,
                project=project,
                project_api_id=project_api_id
            )
        )

    # Perform bulk_create with update_conflicts for upsert
    if board_objects_to_save:
        # The 'fields' argument specifies which unique constraint to check for conflicts.
        # It must match a unique field or a UniqueConstraint.
        # If a conflict occurs on 'api_id', then the 'update_fields' will be applied.
        created_count = Board.objects.bulk_create(
            board_objects_to_save,
            update_conflicts=True,
            unique_fields=['api_id'], # The field(s) used to detect a conflict
            update_fields=['title', 'project'] # The fields to update if a conflict occurs
        )
        print(f"Successfully processed {len(board_objects_to_save)} boards (created/updated).")
        # Note: bulk_create with update_conflicts returns the number of objects created on some backends,
        # but for others (like PostgreSQL) it returns the number of *inserted* rows, not including updates.
        # So, it's harder to get exact counts of created vs. updated from the return value.

def fetch_and_save_boards(company):
    result = fetch_boards(company)
    if result and 'content' in result:
        save_boards(result['content'])
        return True
    return False

def fetch_and_save_all_companies_boards():
    companies = ['dartlab','prosoft','product','pm']
    results =[]
    for company in companies:
        res = fetch_and_save_boards(company)
        results.append(res)
    return results
