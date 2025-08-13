from django.contrib.auth import get_user_model
import logging
from yougile.services.yg_api_client import ExternalApiClient, ExternalApiException
from django.core.exceptions import ObjectDoesNotExist
from account.models import Profile
from unidecode import unidecode

logger = logging.getLogger(__name__)

def fetch_users(company):
    """
    Fetches users using the common API client.
    """
    try:
        api_client = ExternalApiClient(company=company)
        # Just specify the endpoint relative to the base URL
        data = api_client.get("/users")
        return data
    except ExternalApiException as e:
        logger.error(f"Failed to fetch users: {e.message} (Status: {e.status_code})")
        # Re-raise or handle as per your application's error strategy
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching users: {e}")
        raise

def save_users(users):
    for item in users:
        full_name = item['realName']
        first_name, last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, '')
        User = get_user_model()

        try:
            user = User.objects.get(email=item['email'])
            # If the user exists, update their details
            user.first_name = first_name
            user.last_name = last_name
            user.username = unidecode(first_name.lower())
            user.save()
            profile = user.profile
            profile.yougile_id = item['id']
            profile.save()
            print(f"An existing user was updated {user.username}")

        except ObjectDoesNotExist:
            # If the user does not exist, create a new one with a password
            login = unidecode(first_name.lower())
            if login == 'marat':
                login = login + '2'
            user = User.objects.create_user(
                email=item['email'],
                password=first_name,
                first_name=first_name,
                last_name=last_name,
                username=login,
                # Depending on your user model, you might need to provide a username
                # username=email,
            )
            print(f"A new user was created with a password {user.username}.")
            Profile.objects.create(user=user, yougile_id=item['id'])
            print("A new profile was also created.")



def fetch_and_save_users(company):
    result = fetch_users(company)
    if result and 'content' in result:
        save_users(result['content'])
        return True
    return False

def fetch_and_save_all_companies_users():
    companies = ['dartlab','prosoft','product','pm']
    results =[]
    for company in companies:
        res = fetch_and_save_users(company)
        results.append(res)
    return results