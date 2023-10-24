import os
import requests
import re
from dotenv import load_dotenv
from custom_logging import print_error, print_success

load_dotenv()

# Read organization and personal access token from the .env file
organization = os.getenv("CREATE_GITHUB_TEAMS_FOR_EACH_REPO_AND_ACCESS_LEVEL__ORGANIZATION")
personal_access_token = os.getenv("CREATE_GITHUB_TEAMS_FOR_EACH_REPO_AND_ACCESS_LEVEL__TOKEN")

# Regular expression to match team names
regex_pattern = r"(.*)__temp"

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
            new_team_name = match.group(1) + "__reviewers"
            rename_url = f"https://api.github.com/teams/{team['id']}"
            data = {
                "name": new_team_name,
            }
            response = requests.patch(rename_url, headers=headers, json=data)
            if response.status_code == 200:
                print_success(f"Renamed team '{team_name}' to '{new_team_name}'")
            else:
                print_error(f"Failed to rename team '{team_name}', Response Code: {response.status_code}, Response: {response.text}")
else:
    print_error(f"Failed to retrieve the list of teams, Response Code: {response.status_code}, Response: {response.text}")
