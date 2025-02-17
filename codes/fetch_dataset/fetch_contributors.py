# This Python script fetches contributor data from specified GitHub repositories using the GitHub API
# and saves the collected information into CSV and JSON files. 
# It retrieves details such as the number of pull requests submitted and merged, issues opened, 
# repositories contributed to, follower count, stars received on personal repositories, account age, 
# and whether the user is a member of the organization. 

import requests
import json
import csv
from datetime import datetime

TOKEN = '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'  # GitHub Personal Access Token
HEADERS = {'Authorization': f'token {TOKEN}'}  # header for the request
REPOSITORIES = ['netdata/netdata']  # Replace with targeted repo


def get_user_details(username):
    """Fetch user details from GitHub API."""
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch user details for {username}")
        return None
    return response.json()


def get_user_activity(username):
    """Fetch contributor activity (PRs, issues, repos) from GitHub API."""
    total_prs = 0
    total_merged_prs = 0
    total_issues = 0
    total_repositories = 0

    # Count total PRs submitted
    url = f'https://api.github.com/search/issues?q=author:{username}+type:pr'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        total_prs = len(response.json().get('items', []))

    # Count total PRs merged
    url = f'https://api.github.com/search/issues?q=author:{username}+is:merged+type:pr'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        total_merged_prs = len(response.json().get('items', []))

    # Count total issues opened
    url = f'https://api.github.com/search/issues?q=author:{username}+type:issue'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        total_issues = len(response.json().get('items', []))

    # Get total repositories contributed to (distinct repositories)
    url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        total_repositories = len(response.json())

    return total_prs, total_merged_prs, total_issues, total_repositories


def get_user_reputation(username):
    """Fetch contributor reputation (followers, stars) from GitHub API."""
    user_details = get_user_details(username)
    if user_details:
        followers = user_details.get('followers', 0)
        repos_url = user_details.get('repos_url')
        stars_received = 0

        # Fetch all repositories of the user
        response = requests.get(repos_url, headers=HEADERS)
        if response.status_code == 200:
            repos = response.json()
            # Sum stars from all user repositories
            stars_received = sum([repo['stargazers_count'] for repo in repos])

        return followers, stars_received
    return 0, 0


def get_contributor_affiliation(username, org):
    """Check if the contributor is a member of an organization."""
    url = f'https://api.github.com/orgs/{org}/members/{username}'
    response = requests.get(url, headers=HEADERS)
    return response.status_code == 204  # 204 means the user is a member


def fetch_contributors(repo, org):
    """Fetch contributors for a GitHub repository and save to CSV and JSON."""
    url = f'https://api.github.com/repos/{repo}/contributors'
    contributors_csv_file = f'{repo.replace("/", "-")}-contributors.csv'
    contributors_json_file = f'{repo.replace("/", "-")}-contributors.json'
    contributors_data = []

    page = 1
    while True:
        # Make a request for a specific page
        response = requests.get(url, headers=HEADERS, params={'page': page, 'per_page': 100})

        if response.status_code != 200:
            print(f"Failed to fetch contributors for {repo}: {response.status_code}")
            return

        # Fetch contributors in a list of JSON
        contributors = response.json()

        if not contributors:  # No more contributors left to fetch
            break

        # Open the files in append mode
        with open(contributors_csv_file, 'a', newline='', encoding='utf-8') as csvfile, \
                open(contributors_json_file, 'a', encoding='utf-8') as jsonfile:

            csv_writer = csv.writer(csvfile)

            # If it’s the first page, write the header
            if page == 1:
                csv_writer.writerow([
                    'Login', 'Contributions', 'URL', 'Type', 'Site Admin',
                    'Account Age (days)', 'Total PRs Submitted', 'Total PRs Merged',
                    'Total Issues Opened', 'Total Repositories Contributed To',
                    'Followers', 'Stars Received', 'Is Member of Organization'
                ])

            # Loop through all the contributors
            for contributor in contributors:
                login = contributor.get('login')
                contributions = contributor.get('contributions')
                user_url = contributor.get('html_url')
                user_type = contributor.get('type')
                site_admin = contributor.get('site_admin')

                # Get detailed user information
                user_details = get_user_details(login)
                if user_details:
                    account_creation_date = user_details.get('created_at')
                    account_age = (datetime.now() - datetime.strptime(account_creation_date, "%Y-%m-%dT%H:%M:%SZ")).days

                    activity_history = get_user_activity(login)
                    reputation = get_user_reputation(login)
                    affiliation = get_contributor_affiliation(login, org)

                    # Build contributor profile
                    contributor_entry = {
                        'Login': login,
                        'Contributions': contributions,
                        'URL': user_url,
                        'Type': user_type,
                        'Site Admin': site_admin,
                        'Account Age (days)': account_age,
                        'Total PRs Submitted': activity_history[0],
                        'Total PRs Merged': activity_history[1],
                        'Total Issues Opened': activity_history[2],
                        'Total Repositories Contributed To': activity_history[3],
                        'Followers': reputation[0],
                        'Stars Received': reputation[1],
                        'Is Member of Organization': affiliation
                    }

                    contributors_data.append(contributor_entry)

                    # Write contributor data to CSV
                    csv_writer.writerow([
                        contributor_entry['Login'],
                        contributor_entry['Contributions'],
                        contributor_entry['URL'],
                        contributor_entry['Type'],
                        contributor_entry['Site Admin'],
                        contributor_entry['Account Age (days)'],
                        contributor_entry['Total PRs Submitted'],
                        contributor_entry['Total PRs Merged'],
                        contributor_entry['Total Issues Opened'],
                        contributor_entry['Total Repositories Contributed To'],
                        contributor_entry['Followers'],
                        contributor_entry['Stars Received'],
                        contributor_entry['Is Member of Organization']
                    ])

            # Append contributor data to JSON
            json.dump(contributors_data, jsonfile, indent=4)

        # Check for the "Link" header to find the next page
        if 'Link' in response.headers:
            links = response.headers['Link']
            # Look for the 'rel="next"' part to get the next page URL
            if 'rel="next"' in links:
                page += 1
            else:
                break
        else:
            break

    print(f"Contributors data saved for {repo}.")


for repository in REPOSITORIES:
    print(f"Fetching contributors for repository: {repository}")
    fetch_contributors(repository, 'netdata')  # Replace with the actual organization name
    print(f"Finished fetching contributors for: {repository}")
