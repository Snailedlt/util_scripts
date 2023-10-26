import os
import requests
import re
from dotenv import load_dotenv
from custom_logging import print_error, print_warning, print_success

load_dotenv()

# Read organization and personal access token from the .env file
organization = os.getenv("ORGANIZATION")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")

# Regular expression to match team names
regex_pattern = r".*__reviewers"

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
        repo_name = team["name"].replace("__reviewers", "")
        description = team["description"]
        if re.match(regex_pattern, team_name):
            # Generate the URL for updating the team's description
            update_url = f"https://api.github.com/teams/{team['id']}"

            # New team description data with {team_name} variable
            new_description = f"Reviewers for the {repo_name} repo. Use this team for PR reviews"
            data = {
                "description": new_description,
            }

            # Make the request to update the team's description
            response = requests.patch(update_url, headers=headers, json=data)

            if response.status_code == 200:
                print_success(f"Updated description of team '{team_name}'")
            else:
                print_error(f"Failed to update description of team '{team_name}'")
else:
    print_error("Failed to retrieve the list of teams")
