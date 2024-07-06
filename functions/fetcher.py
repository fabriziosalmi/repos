import requests
from datetime import datetime
from .config import GITHUB_USERNAME, BASE_URL

def fetch_repositories_with_stars(min_stars=1):
    url = BASE_URL
    params = {
        'per_page': 100,  # maximum items per page
        'page': 1,        # start with first page
    }
    repositories = []

    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            repos = response.json()
            for repo in repos:
                if repo['stargazers_count'] >= min_stars and not repo['archived']:
                    repositories.append(repo)
            if 'next' in response.links.keys():
                url = response.links['next']['url']
                params['page'] += 1
            else:
                break
        else:
            print(f'Failed to fetch repositories. Status code: {response.status_code}')
            break

    # Sort repositories by stars (descending)
    repositories.sort(key=lambda x: x['stargazers_count'], reverse=True)

    return repositories

def fetch_latest_commit_date(repo_name):
    url = f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/commits'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            commits = response.json()
            if commits:
                latest_commit_date = commits[0]['commit']['committer']['date']
                return datetime.strptime(latest_commit_date, '%Y-%m-%dT%H:%M:%SZ')
        else:
            print(f'Failed to fetch commits for {repo_name}. Status code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error fetching commits for {repo_name}: {e}')
    
    return None
