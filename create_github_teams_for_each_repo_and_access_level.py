#TODO: Fix the issue where the response is 422 but the team doesn't exist

from dotenv import load_dotenv
from custom_logging import print_error, print_success, print_warning  # Import functions from custom_logging
import requests
import os

load_dotenv()

# Fill these in in the .env file
organization = os.getenv("ORGANIZATION")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN") # Must have repo and admin:org scopes

# valid roles are "admin", "maintain", "push", "triage", "pull"
# valid permissions are "admin", "maintain", "push", "triage", "pull"
roles_and_permissions = {
    "admin": "admin",
    "maintain": "maintain",
    "write": "push",
    "triage": "triage"
}

# Get the list of repositories in the organization
repositories_url = f"https://api.github.com/orgs/{organization}/repos"
headers = {
    "Authorization": f"Bearer {personal_access_token}",
    "Accept": "application/vnd.github.v3+json",
}

response = requests.get(repositories_url, headers=headers)

if response.status_code != 200:
    print_error(f"Failed to fetch repositories for the organization. Status code:", response.status_code)
    print(response.text)
    exit(1)

repositories = [repo["name"] for repo in response.json()]

# Create root-level teams for each repository
for repo in repositories:
    root_team_name = repo + "__reviewers"
    root_team_description = f"Root-level team for {repo}"

    root_team_url = f"https://api.github.com/orgs/{organization}/teams"
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    root_team_data = {
        "name": root_team_name,
        "description": root_team_description,
        "privacy": "closed",  # Change to "secret" if desired
    }
    root_team_id = ""

    root_team_response = requests.post(root_team_url, json=root_team_data, headers=headers)

    if root_team_response.status_code == 201:
        print_success(f"Root-level team '{root_team_name}' created successfully for '{repo}'.")
        root_team_id = root_team_response.json()["id"]
    elif root_team_response.status_code == 422:
        print_warning(f"Root-level team '{root_team_name}' already exists for '{repo}'... Fetching ID.")
        # Get the ID of the existing team via rest API
        root_team_id = requests.get(root_team_url + "/" + root_team_name, headers=headers).json()["id"]
    else:
        print_error(f"Failed to create root-level team for '{repo}'. Status code:", root_team_response.status_code)
        print(root_team_response.text)

    print("root_team_id:", root_team_id)

    # Create child teams for different access levels
    for role, permission in roles_and_permissions.items():
        print("role:", role)
        print("permission:", permission)
        child_team_name = f"{repo}__{role.capitalize()}"
        child_team_description = f"Team with {role} access to the {repo} repository"

        child_team_url = f"https://api.github.com/orgs/{organization}/teams"
        child_team_data = {
            "name": child_team_name,
            "description": child_team_description,
            "privacy": "closed",  # Change to "secret" if desired
            "parent_team_id": root_team_id,  # Set the parent team for nesting
            "permission": permission
        }
        print("child_team_data:", child_team_data)
        child_team_response = requests.post(child_team_url, json=child_team_data, headers=headers)

        if child_team_response.status_code == 201:
            print_success(f"Child team '{child_team_name}' created successfully for '{repo}'.")
        elif child_team_response.status_code == 422:
            print_warning(f"Child team '{child_team_name}' already exists for '{repo}'.")
            # print response
            print(child_team_response.text)
        else:
            print_error(f"Failed to create child team for '{repo}'. Status code:", child_team_response.status_code)
            print(child_team_response.text)
