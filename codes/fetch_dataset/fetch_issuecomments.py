# This Python script fetches comments from closed issues in specified GitHub repositories using the GitHub API
# and saves the collected information into CSV and JSON files. 
# It retrieves details such as the issue ID, issue state, issue title, comment ID, author, comment creation date, 
# and the comment body (truncated to 5000 characters). 

import csv
import json
import requests

TOKEN = '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'  # GitHub Personal Access Token
HEADERS = {'Authorization': f'token {TOKEN}'} # header for the request
REPOSITORIES = ['netdata/netdata']  # Replace with targeted repo
# additional params to access specific types of data
PARAMS = {
    'state': 'closed',
    'since': '2022-01-01T00:00:00Z',
    'sort': 'updated'
}

def fetch_comments_with_issue_info(repo):
    csv_file = f'{repo.replace("/", "-")}-comments.csv'
    json_file = f'{repo.replace("/", "-")}-comments.json'
    comments_data = []

    issues_url = f'https://api.github.com/repos/{repo}/issues'
    response = requests.get(issues_url, params=PARAMS, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.json()}")

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Issue ID', 'Issue State', 'Issue Title', 'Comment ID', 'Author', 'Created At', 'Comment Body'])

        # looping through each issue
        for issue in response.json():
            if issue['comments'] > 0:  # Process only if comments exist
                comments_url = issue['comments_url'] # fetching comment links
                comments_response = requests.get(comments_url, headers=HEADERS)
                if comments_response.status_code != 200:
                    raise Exception(f"Error {comments_response.status_code}: {comments_response.json()}")

                for comment in comments_response.json():
                    row = [
                        issue['number'],
                        issue['state'],
                        issue['title'],
                        comment['id'],
                        comment['user']['login'],
                        comment['created_at'],
                        comment['body'][:5000]
                    ]
                    writer.writerow(row)
                    comments_data.append({
                        'Issue ID': issue['number'],
                        'Issue State': issue['state'],
                        'Issue Title': issue['title'],
                        'Comment ID': comment['id'],
                        'Author': comment['user']['login'],
                        'Created At': comment['created_at'],
                        'Comment Body': comment['body'][:5000]
                    })

    with open(json_file, 'w', encoding='utf-8') as jf:
        json.dump(comments_data, jf, indent=4)

for repository in REPOSITORIES:
    print(f"Processing comments with issue information for repository: {repository}")
    fetch_comments_with_issue_info(repository)
    print(f"Finished processing comments with issue information for: {repository}")