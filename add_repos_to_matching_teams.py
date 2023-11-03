"""
A script to add repositories to all teams that match a regex based on the team
name.

For example:
If the regex is r"(.*)__reviewers" then the match from the
regex will be the repository name. Add the repository with that repository
name to that repo.
"""

import os
import requests
import re
from dotenv import load_dotenv
from custom_logging import print_error, print_success

load_dotenv()

# Read organization and personal access token from the .env file
organization = os.getenv("ORGANIZATION")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")

# Regular expression to match team names
regex_pattern = r"(.*)__reviewers"

# GitHub API URL for listing teams in the organization
url = f"https://api.github.com/orgs/{organization}/teams"

# Make the request to list teams
headers = {
    "Authorization": f"token {personal_access_token}",
    "Accept": "application/vnd.github.v3+json",
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    teams = response.json()
    for team in teams:
        team_name = team["name"]
        match = re.match(regex_pattern, team_name)
        if match:
            repo_name = match.group(1)
            add_repo_url = f"https://api.github.com/teams/{team['id']}/repos/{organization}/{repo_name}"
            response = requests.put(add_repo_url, headers=headers)
            if response.status_code == 204:
                print_success(f"Added {repo_name} to {team_name}")
            else:
                print_error(f"Failed to add {repo_name} to {team_name}")
else:
    print_error("Failed to list teams")
