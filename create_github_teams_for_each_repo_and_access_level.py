import os
import requests
from dotenv import load_dotenv
load_dotenv()

# ANSI escape codes for text colors
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"  # Reset text color to default

# Fill these in in the .env file
organization = os.getenv("CREATE_GITHUB_TEAMS_FOR_EACH_REPO_AND_ACCESS_LEVEL__ORGANIZATION")
personal_access_token = os.getenv("CREATE_GITHUB_TEAMS_FOR_EACH_REPO_AND_ACCESS_LEVEL__TOKEN") # Must have repo and admin:org scopes

# valid roles are "admin", "maintain", "triage", "push", "pull"
roles = ["admin", "maintain", "triage"]

# Get the list of repositories in the organization
repositories_url = f"https://api.github.com/orgs/{organization}/repos"
headers = {
    "Authorization": f"Bearer {personal_access_token}",
    "Accept": "application/vnd.github.v3+json",
}

response = requests.get(repositories_url, headers=headers)

if response.status_code != 200:
    print(f"Failed to fetch repositories for the organization. Status code:", response.status_code)
    print(response.text)
    exit(1)

repositories = [repo["name"] for repo in response.json()]

# Create root-level teams for each repository
for repo in repositories:
    root_team_name = repo
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

    root_team_response = requests.post(root_team_url, json=root_team_data, headers=headers)

    if root_team_response.status_code == 201:
        print(f"{GREEN}Root-level team '{root_team_name}' created successfully for '{repo}'.{RESET}")
        root_team_id = root_team_response.json()["id"]
    elif root_team_response.status_code == 422:
        print(f"{YELLOW}Root-level team '{root_team_name}' already exists for '{repo}'.{RESET}")
    else:
        print(f"{RED}Failed to create root-level team for '{repo}'. Status code:", root_team_response.status_code + RESET)
        print(root_team_response.text)
        continue

    # Create child teams for different access levels
    for role in roles:
        child_team_name = f"{repo}__{role.capitalize()}"
        child_team_description = f"Team with {role} access to the {repo} repository"

        child_team_url = f"https://api.github.com/orgs/{organization}/teams"
        child_team_data = {
            "name": child_team_name,
            "description": child_team_description,
            "privacy": "closed",  # Change to "secret" if desired
            "parent_team_id": root_team_id  # Set the parent team for nesting
        }

        child_team_response = requests.post(child_team_url, json=child_team_data, headers=headers)

        if child_team_response.status_code == 201:
            print(f"{GREEN}Child team '{child_team_name}' created successfully for '{repo}'.{RESET}")
        elif child_team_response.status_code == 422:
            print(f"{YELLOW}Child team '{child_team_name}' already exists for '{repo}'.{RESET}")
        else:
            print(f"{RED}Failed to create child team for '{repo}'. Status code:", child_team_response.status_code + RESET)
            print(child_team_response.text)
