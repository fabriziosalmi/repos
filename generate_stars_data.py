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

def fetch_stars(repo_owner, repo_name, token):
    headers = {
        "Authorization": f"token {token}"
    }
    url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/stargazers"
    response = requests.get(url, headers=headers, params={'per_page': 100})
    if response.status_code != 200:
        raise Exception(f"Failed to fetch stars: {response.status_code}")
    return response.json()

def count_stars_last_month(repos, token):
    one_month_ago = datetime.now() - timedelta(days=30)
    total_stars = 0

    for repo in repos:
        stargazers = fetch_stars(USER, repo['name'], token)
        star_dates = [datetime.strptime(stargazer['starred_at'], '%Y-%m-%dT%H:%M:%SZ') for stargazer in stargazers if 'starred_at' in stargazer]
        total_stars += sum(1 for date in star_dates if date > one_month_ago)
    
    return total_stars

def generate_json(star_count):
    data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "stars_last_month": star_count
    }
    os.makedirs('data', exist_ok=True)
    with open('data/stars.json', 'w') as f:
        json.dump(data, f, indent=4)

def generate_graph():
    with open('data/stars.json') as f:
        data = json.load(f)
    dates = [data['date']]
    stars = [data['stars_last_month']]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, stars, marker='o')
    plt.title('Total Stars in the Last Month')
    plt.xlabel('Date')
    plt.ylabel('Stars')
    plt.grid(True)
    plt.savefig('data/stars_graph.png')

def main():
    repos = fetch_repos(USER, TOKEN)
    star_count = count_stars_last_month(repos, TOKEN)
    generate_json(star_count)
    generate_graph()

if __name__ == '__main__':
    main()
