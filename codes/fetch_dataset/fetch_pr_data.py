# Code to fetch data from a Github repo (pr_number,lines_added,lines_deleted,comments,review_comments,avg_review_comments,state,merged,accepted)

import requests
import csv

# Replace with your GitHub token for authentication
GITHUB_TOKEN = " " #insert token here
REPO_NAME = "angular/angular"  # Replace with the actual owner/repo name

# GitHub API URL for Pull Requests
API_URL = f"https://api.github.com/repos/{REPO_NAME}/pulls"

# Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}

def get_pull_requests():
    """ Fetch all pull requests from the repository """
    print("Fetching pull requests...")
    prs = []
    page = 1
    while True:
        response = requests.get(f"{API_URL}?state=all&per_page=100&page={page}", headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching PRs: {response.json()}")
            break
        data = response.json()
        if not data:
            break
        prs.extend(data)
        print(f"Fetched {len(data)} PRs from page {page}...")
        page += 1
    print(f"Total PRs fetched: {len(prs)}")
    return prs

def get_pr_stats(pr_number):
    """ Get additional statistics from a specific pull request """
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls/{pr_number}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        pr_data = response.json()
        merged = pr_data.get("merged_at") is not None
        return {
            "lines_added": pr_data.get("additions", 0),
            "lines_deleted": pr_data.get("deletions", 0),
            "comments": pr_data.get("comments", 0),
            "review_comments": pr_data.get("review_comments", 0),
            "commits": pr_data.get("commits", 1),
            "merged": merged,
            "state": pr_data.get("state"),
            "accepted": merged
        }
    return {}

def save_to_csv(pr_stats, mode="w"):
    """ Save the PR stats to a dynamically named CSV file """
    filename = f"pull_requests_{REPO_NAME.replace('/', '_')}.csv"
    file_exists = mode == "a"
    with open(filename, mode=mode, newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["pr_number", "lines_added", "lines_deleted", "comments", "review_comments", "avg_review_comments", "state", "merged", "accepted"])
        for pr in pr_stats:
            writer.writerow([
                pr["pr_number"], pr["lines_added"], pr["lines_deleted"], pr["comments"],
                pr["review_comments"], pr["avg_review_comments"], pr["state"], pr["merged"], pr["accepted"]
            ])

def main():
    print("Starting script...")
    prs = get_pull_requests()
    filename = f"pull_requests_{REPO_NAME.replace('/', '_')}.csv"
    pr_stats = []
    mode = "w"  # Overwrite file initially

    for index, pr in enumerate(prs, start=1):
        stats = get_pr_stats(pr["number"])
        if stats:
            avg_review_comments = stats["review_comments"] / stats["commits"] if stats["commits"] > 0 else 0
            pr_data = {
                "pr_number": pr["number"],
                "lines_added": stats["lines_added"],
                "lines_deleted": stats["lines_deleted"],
                "comments": stats["comments"],
                "review_comments": stats["review_comments"],
                "avg_review_comments": avg_review_comments,
                "state": stats["state"],
                "merged": stats["merged"],
                "accepted": stats["accepted"]
            }
            pr_stats.append(pr_data)
            save_to_csv([pr_data], mode="a")  # Append each PR data immediately to CSV
        if index % 10 == 0 or index == len(prs):  # Print progress every 10 PRs
            print(f"Processed {index}/{len(prs)} PRs...")
    print("Script completed.")

if __name__ == "__main__":
    main()
