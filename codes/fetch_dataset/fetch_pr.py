# This Python script fetches pull request (PR) and project context data from specified GitHub repositories using the GitHub API 
# and saves the collected information into CSV and JSON files. 
# It retrieves details such as PR author, title, state, creation and merge dates, number of files changed, lines added/deleted, 
# total commits, comments, review comments, requested reviewers, and linked issues. 
# Additionally, it collects repository-level metadata, including repository size, stars, forks, contributor count, and commit activity. 

import requests
import json
import csv
from datetime import datetime

TOKEN = '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'  # GitHub Personal Access Token
HEADERS = {'Authorization': f'token {TOKEN}'}  # header for the request
REPOSITORIES = ['netdata/netdata']  # Replace with targeted repo

def get_repository_data(repo):
    """Fetch repository data (size, stars, forks, contributors, commits)"""
    url = f'https://api.github.com/repos/{repo}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch repository data for {repo}")
        return None
    return response.json()

def fetch_pr_and_project_context(repo):
    """Fetch PR and Project Context Data for a GitHub repository and save to CSV and JSON."""
    url = f'https://api.github.com/repos/{repo}/pulls'
    prs_csv_file = f'{repo.replace("/", "-")}-prs.csv'
    prs_json_file = f'{repo.replace("/", "-")}-prs.json'
    prs_data = []

    page = 1
    while True:
        response = requests.get(url, headers=HEADERS, params={'page': page, 'per_page': 100, 'state': 'all'})

        if response.status_code != 200:
            print(f"Failed to fetch PRs for {repo}: {response.status_code}")
            return

        prs = response.json()

        if not prs:
            break

        with open(prs_csv_file, 'a', newline='', encoding='utf-8') as csvfile, \
                open(prs_json_file, 'a', encoding='utf-8') as jsonfile:

            csv_writer = csv.writer(csvfile)

            if page == 1:
                csv_writer.writerow([
                    'PR ID', 'PR Author', 'Title', 'State', 'Created At', 'Merged At', 'Closed At',
                    'Labels', 'Base Branch', 'Head Branch', 'Files Changed', 'Lines Added',
                    'Lines Deleted', 'Commits', 'Comments', 'Review Comments', 'Reviewers',
                    'Review States', 'Draft Status', 'Linked Issues', 'Repository ID',
                    'Repository Size (Stars, Forks, Contributors, Commits)',
                    'Repository Activity (Commits, PRs, Issues)', 'Project Phase (Before Major Release, After Major Release, Active Phase)'
                ])

            for pr in prs:
                pr_id = pr.get('id')
                pr_author = pr.get('user', {}).get('login', 'N/A')  # Fetching PR Author
                title = pr.get('title')
                state = pr.get('state')
                created_at = pr.get('created_at')
                merged_at = pr.get('merged_at')
                closed_at = pr.get('closed_at')
                labels = ', '.join([label['name'] for label in pr.get('labels', [])])
                base_branch = pr.get('base', {}).get('ref')
                head_branch = pr.get('head', {}).get('ref')
                files_changed = pr.get('changed_files')
                lines_added = pr.get('additions')
                lines_deleted = pr.get('deletions')
                commits = pr.get('commits')
                comments = pr.get('comments')
                review_comments = pr.get('review_comments')
                reviewers = ', '.join([reviewer['login'] for reviewer in pr.get('requested_reviewers', [])])
                review_states = ', '.join([review['state'] for review in pr.get('reviews', [])])
                draft_status = pr.get('draft')
                linked_issues = ', '.join([issue['url'] for issue in pr.get('linked_issues', [])])

                repo_data = get_repository_data(repo)
                repo_id = repo_data.get('id') if repo_data else None
                stars = repo_data.get('stargazers_count') if repo_data else 0
                forks = repo_data.get('forks_count') if repo_data else 0
                contributors = repo_data.get('contributors_count') if repo_data else 0
                total_commits = repo_data.get('commit_count') if repo_data else 0

                pr_entry = {
                    'PR ID': pr_id,
                    'PR Author': pr_author,
                    'Title': title,
                    'State': state,
                    'Created At': created_at,
                    'Merged At': merged_at,
                    'Closed At': closed_at,
                    'Labels': labels,
                    'Base Branch': base_branch,
                    'Head Branch': head_branch,
                    'Files Changed': files_changed,
                    'Lines Added': lines_added,
                    'Lines Deleted': lines_deleted,
                    'Commits': commits,
                    'Comments': comments,
                    'Review Comments': review_comments,
                    'Reviewers': reviewers,
                    'Review States': review_states,
                    'Draft Status': draft_status,
                    'Linked Issues': linked_issues,
                    'Repository ID': repo_id,
                    'Repository Size (Stars, Forks, Contributors, Commits)': f"{stars}, {forks}, {contributors}, {total_commits}"
                }

                prs_data.append(pr_entry)

                csv_writer.writerow([
                    pr_entry['PR ID'], pr_entry['PR Author'], pr_entry['Title'], pr_entry['State'], pr_entry['Created At'], pr_entry['Merged At'],
                    pr_entry['Closed At'], pr_entry['Labels'], pr_entry['Base Branch'], pr_entry['Head Branch'],
                    pr_entry['Files Changed'], pr_entry['Lines Added'], pr_entry['Lines Deleted'], pr_entry['Commits'],
                    pr_entry['Comments'], pr_entry['Review Comments'], pr_entry['Reviewers'], pr_entry['Review States'],
                    pr_entry['Draft Status'], pr_entry['Linked Issues'], pr_entry['Repository ID'],
                    pr_entry['Repository Size (Stars, Forks, Contributors, Commits)']
                ])

            json.dump(prs_data, jsonfile, indent=4)

        if 'Link' in response.headers:
            links = response.headers['Link']
            if 'rel="next"' in links:
                page += 1
            else:
                break
        else:
            break

    print(f"PR and Project Context data saved for {repo}.")

for repository in REPOSITORIES:
    print(f"Fetching PR and Project Context data for repository: {repository}")
    fetch_pr_and_project_context(repository)
    print(f"Finished fetching PR and Project Context data for: {repository}")
