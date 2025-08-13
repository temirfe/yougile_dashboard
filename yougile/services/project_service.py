from yougile.models import Project
import logging
from yougile.services.yg_api_client import ExternalApiClient, ExternalApiException


logger = logging.getLogger(__name__)

def fetch_projects(company='dartlab'):
    """
    Fetches projects using the common API client.
    """
    try:
        api_client = ExternalApiClient(company=company)
        # Just specify the endpoint relative to the base URL
        projects_data = api_client.get("/projects")
        return projects_data
    except ExternalApiException as e:
        logger.error(f"Failed to fetch projects: {e.message} (Status: {e.status_code})")
        # Re-raise or handle as per your application's error strategy
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching projects: {e}")
        raise

def create_project_via_api(project_data):
    """
    Creates a project via the external API.
    """
    try:
        api_client = ExternalApiClient()
        response_data = api_client.post("/projects", data=project_data)
        return response_data
    except ExternalApiException as e:
        logger.error(f"Failed to create project via API: {e.message} (Status: {e.status_code})")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating project via API: {e}")
        raise

def save_projects(projects,company):
    for project_data in projects:
        try:
            # 'api_id' is used to look up the existing project.
            # 'defaults' specifies values to update if the object exists, or to set if a new one is created.
            project, created = Project.objects.update_or_create(
                api_id=project_data['id'],
                defaults={'title': project_data['title'],'company':company}
            )
            # 'project' is the instance, 'created' is a boolean (True if created, False if updated)
        except Exception as e:
            # Example of basic error handling
            logger.error(f"Error processing project {project_data.get('id', 'N/A')}: {e}")

def fetch_and_save_projects(company):
    result = fetch_projects(company)
    if result and 'content' in result:
        save_projects(result['content'],company)
        return True
    return False

def fetch_and_save_all_companies_projects():
    companies = ['dartlab','prosoft','product','pm']
    results =[]
    for company in companies:
        res = fetch_and_save_projects(company)
        results.append(res)
    return results
