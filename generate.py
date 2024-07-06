import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

GITHUB_USERNAME = 'fabriziosalmi'

def fetch_repositories_with_stars(min_stars=5):
    url = f'https://api.github.com/users/{GITHUB_USERNAME}/repos'
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
                if repo['stargazers_count'] >= min_stars:
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

def generate_html_page(repositories):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My GitHub Repositories</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <h1>My GitHub Repositories</h1>
        <table>
            <tr>
                <th>Repository</th>
                <th>Latest Commit</th>
                <th>Stars</th>
            </tr>
    '''

    for repo in repositories:
        repo_name = repo['name']
        repo_url = repo['html_url']
        latest_commit_date = fetch_latest_commit_date(repo_name)
        stars_count = repo['stargazers_count']

        if latest_commit_date:
            latest_commit_date_str = latest_commit_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            latest_commit_date_str = 'N/A'

        html_content += f'''
            <tr>
                <td><a href="{repo_url}" target="_blank">{repo_name}</a></td>
                <td>{latest_commit_date_str}</td>
                <td>{stars_count}</td>
            </tr>
        '''

    html_content += '''
        </table>
    </body>
    </html>
    '''

    with open('docs/index.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    print('GitHub repositories HTML page generated: docs/index.html')

def main():
    repositories = fetch_repositories_with_stars(min_stars=5)
    generate_html_page(repositories)

if __name__ == '__main__':
    main()
