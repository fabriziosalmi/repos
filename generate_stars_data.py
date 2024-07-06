import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# Constants
GITHUB_API_URL = "https://api.github.com"
USER = "fabriziosalmi"  # Replace with your GitHub username
TOKEN = os.getenv("GITHUB_TOKEN")  # GitHub token from environment variable

def fetch_repos(user, token):
    headers = {
        "Authorization": f"token {token}"
    }
    url = f"{GITHUB_API_URL}/users/{user}/repos"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {response.status_code}")
    return response.json()

def fetch_starred_dates(user, repo_name, token):
    headers = {
        "Authorization": f"token {token}"
    }
    url = f"{GITHUB_API_URL}/repos/{user}/{repo_name}/stargazers"
    starred_dates = []
    page = 1
    while True:
        response = requests.get(url, headers=headers, params={'per_page': 100, 'page': page})
        if response.status_code != 200:
            raise Exception(f"Failed to fetch stargazers: {response.status_code}")
        stargazers = response.json()
        if not stargazers:
            break
        for stargazer in stargazers:
            starred_date = stargazer['starred_at']
            starred_dates.append(starred_date)
        page += 1
    return starred_dates

def count_daily_stars(repos, token):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    daily_stars = {start_date + timedelta(days=i): 0 for i in range(181)}

    for repo in repos:
        stargazers = fetch_starred_dates(USER, repo['name'], token)
        for starred_at in stargazers:
            starred_at_date = datetime.strptime(starred_at, '%Y-%m-%dT%H:%M:%SZ').date()
            if start_date.date() <= starred_at_date <= end_date.date():
                daily_stars[starred_at_date] += 1

    total_stars = 0
    daily_total_stars = {}
    for date in sorted(daily_stars):
        total_stars += daily_stars[date]
        daily_total_stars[date.strftime('%Y-%m-%d')] = total_stars

    return daily_total_stars

def generate_json(daily_total_stars):
    data = {
        "daily_total_stars": daily_total_stars
    }
    os.makedirs('data', exist_ok=True)
    with open('data/stars.json', 'w') as f:
        json.dump(data, f, indent=4)

def generate_graph():
    with open('data/stars.json') as f:
        data = json.load(f)

    dates = list(data['daily_total_stars'].keys())
    stars = list(data['daily_total_stars'].values())

    plt.figure(figsize=(10, 5))
    plt.plot(dates, stars, marker='o')
    plt.title('Total Repository Stars Count in the Last 6 Months')
    plt.xlabel('Date')
    plt.ylabel('Total Stars')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('data/stars_graph.png')

def main():
    repos = fetch_repos(USER, TOKEN)
    daily_total_stars = count_daily_stars(repos, TOKEN)
    generate_json(daily_total_stars)
    generate_graph()

if __name__ == '__main__':
    main()
