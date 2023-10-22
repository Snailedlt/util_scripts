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

# Create teams for each repository and assign roles
for repo in repositories:
    for role in roles:
        # Create a team for the specific role
        team_name = f"{repo}__{role.capitalize()}"  # Use double underscore as a separator
        team_description = f"Team with {role} access to {repo}"

        url = f"https://api.github.com/orgs/{organization}/teams"
        headers = {
            "Authorization": f"Bearer {personal_access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        data = {
            "name": team_name,
            "description": team_description,
            "privacy": "closed",  # Change to "secret" if desired
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            print(f"{GREEN}Team '{team_name}' created successfully for '{repo}'.{RESET}")
            team_id = response.json()["id"]

            # Add the team to the repository with the appropriate role
            repo_url = f"https://api.github.com/teams/{team_id}/repos/{organization}/{repo}"
            data = {"permission": role}

            response = requests.put(repo_url, json=data, headers=headers)

            if response.status_code == 204:
                print(f"{GREEN}Added '{team_name}' to '{repo}' with '{role}' role.{RESET}")
            elif response.status_code == 422:
                print(f"{YELLOW}Team '{team_name}' already exists for '{repo}'.{RESET}")
            else:
                print(f"{RED}Failed to add team '{team_name}' to '{repo}' with '{role}' role. Status code:", response.status_code + RESET)
                print(response.text)
        elif response.status_code == 422:
            print(f"{YELLOW}Team '{team_name}' already exists in the {organization} organization.{RESET}")
        else:
            print(f"{RED}Failed to create team for '{repo}' with role '{role}'. Status code:", response.status_code + RESET)
            print(response.text)
