import requests
import csv
import time

# GitHub API Token - REPLACE with your actual token
TOKEN = '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'

# Authentication headers
HEADERS = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}


response = requests.get("https://api.github.com/user", headers=HEADERS)

if response.status_code == 200:
    print("✅ Authentication successful!")
    print(response.json())  # Shows user info if successful
else:
    print(f"❌ Authentication failed! Status code: {response.status_code}, Message: {response.text}")

# List of repositories (Format: 'owner/repo')
REPOSITORIES = [
    'netdata/netdata',
    'angular/angular',
    'pytorch/pytorch',
    'ethereum/go-ethereum',
    'nodejs/node',
    'microsoft/TypeScript',
    'puppeteer/puppeteer',
    'scrapy/scrapy',
    'starship/starship',
    'moment/moment',
    '996icu/996.ICU',
    'Significant-Gravitas/AutoGPT',
    'vinta/awesome-python',
    'jwasham/coding-interview-university',
    'sindresorhus/awesome',
    'axios/axios',
    'microsoft/PowerToys',
    'excalidraw/excalidraw',
    'rustdesk/rustdesk',
    'gitextensions/gitextensions']

# Output CSV file
OUTPUT_FILE = "github_releases.csv"

def fetch_releases(repo):
    """Fetches all releases for a given GitHub repository."""
    releases = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/releases?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"⚠️ Failed to fetch releases for {repo}: {response.status_code}")
            break

        data = response.json()
        if not data:
            break  # No more releases

        for release in data:
            releases.append({
                "repository": repo,
                "release_id": release.get("id"),
                "tag_name": release.get("tag_name"),
                "release_name": release.get("name"),
                "published_at": release.get("published_at"),
                "created_at": release.get("created_at"),
                "prerelease": release.get("prerelease"),
                "draft": release.get("draft")
            })

        page += 1  # Move to next page

    return releases

def save_releases_to_csv(repositories):
    """Fetches and saves GitHub release data for multiple repositories to a CSV file."""
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["repository", "release_id", "tag_name", "release_name", "published_at", "created_at", "prerelease", "draft"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for repo in repositories:
            print(f"📡 Fetching releases for: {repo}")
            releases = fetch_releases(repo)
            if releases:
                writer.writerows(releases)
                print(f"✅ Saved {len(releases)} releases for {repo}")
            else:
                print(f"⚠️ No releases found for {repo}")

            time.sleep(1)  # Avoid hitting API rate limits

    print(f"\n📂 All release data saved in '{OUTPUT_FILE}'.")

# Run the script
save_releases_to_csv(REPOSITORIES)
