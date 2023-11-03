"""
This script manages permissions for GitHub team repositories based on team names.

Here's how it works:

1. Fetches all teams within a specified GitHub organization.
2. For each team, it retrieves the repositories that the team can access.
3. Checks if the team name includes a role name (options: admin, maintain, write, triage, read).
4. If a role name is found, it checks if the repository already has the corresponding permission.
5. If the repository doesn't have the permission, it updates the repository's permission to match the role in the team name.

Please note:

- Teams without a parent or without a role name in their name are skipped.
- The script uses the GitHub API and requires a personal access token with the necessary permissions.
- The organization name and personal access token are read from environment variables.
"""

import os
import requests
from dotenv import load_dotenv
from custom_logging import print_error, print_success, print_warning

def load_env_variables():
    load_dotenv()
    return os.getenv("ORGANIZATION"), os.getenv("PERSONAL_ACCESS_TOKEN")

def fetch_teams(organization, headers):
    url = f"https://api.github.com/orgs/{organization}/teams"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print_error("Failed to fetch teams")
        exit(1)
    return response.json()

def fetch_repos(team, headers):
    repos_url = f"https://api.github.com/teams/{team['id']}/repos"
    repos_response = requests.get(repos_url, headers=headers)
    if repos_response.status_code != 200:
        print_error(f"Failed to fetch repositories for team {team['name']}. Status code:", repos_response.status_code)
        return None
    return repos_response.json()

def update_repo_permission(repo, team, permission, headers, organization):
    edit_url = f"https://api.github.com/teams/{team['id']}/repos/{organization}/{repo['name']}"
    data = {"permission": permission}
    edit_response = requests.put(edit_url, headers=headers, json=data)
    if edit_response.status_code != 204:
        print_error(f"Failed to update permission for {repo['name']} in {team['name']}")
    else:
        print_success(f"Successfully updated permission for {repo['name']} in {team['name']} to {permission}")

def main():
    organization, personal_access_token = load_env_variables()

    roles_and_permissions = {
        "admin": "admin",
        "maintain": "maintain",
        "write": "push",
        "triage": "triage",
        "read": "pull"
    }

    headers = {
        "Authorization": f"token {personal_access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    teams = fetch_teams(organization, headers)
    for team in teams:
        if team["parent"] is None:
            print_warning(f"Team {team['name']} does not have a parent. Skipping...")
            continue

        repos = fetch_repos(team, headers)
        if repos is None:
            continue

        for repo in repos:
            role_found = False
            for role, permission in roles_and_permissions.items():
                if role in team["name"].lower():
                    role_found = True
                    if repo["permissions"][permission]:
                        print_warning(f"Permission for {repo['name']} in {team['name']} is already {permission}. Skipping...")
                        continue
                    update_repo_permission(repo, team, permission, headers, organization)
            if not role_found:
                print_warning(f"Team {team['name']} does not contain a role name. Skipping...")

if __name__ == "__main__":
    main()
