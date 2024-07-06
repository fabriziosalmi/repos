import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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

def humanize_commit_date(commit_date):
    now = datetime.utcnow()
    diff = now - commit_date

    if diff.days == 0:
        return 'today'
    elif diff.days == 1:
        return 'yesterday'
    elif diff.days < 7:
        return f'{diff.days} days ago'
    elif diff.days < 30:
        weeks = diff.days // 7
        return f'{weeks} {"week" if weeks == 1 else "weeks"} ago'
    elif diff.days < 365:
        months = diff.days // 30
        return f'{months} {"month" if months == 1 else "months"} ago'
    else:
        years = diff.days // 365
        return f'{years} {"year" if years == 1 else "years"} ago'

def generate_html_page(repositories):
    total_stars = sum(repo['stargazers_count'] for repo in repositories)

    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My GitHub repositories</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 800px;
            width: 100%;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            padding: 20px 0;
            margin: 0;
            font-size: 24px;
        }}
        .stars-counter {{
            text-align: center;
            font-size: 20px;
            margin-bottom: 20px;
            color: #ffbf00;
        }}
        .stars-counter .emoji {{
            font-size: 28px;
            margin-right: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f8f8;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        a {{
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
            font-size: 18px;
        }}
        .description {{
            font-size: 12px;
            color: #666;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px;
            margin-right: 5px;
        }}
        .badge-blue {{
            background-color: #007bff;
            color: white;
        }}
        .badge-gray {{
            background-color: #757575;
            color: white;
        }}
        .badge-yellow {{
            background-color: #ffbf00;
            color: white;
        }}
        .badge-green {{
            background-color: #28a745;
            color: white;
        }}
        .badge-red {{
            background-color: #dc3545;
            color: white;
        }}
        @media only screen and (max-width: 600px) {{
            .container {{
                border-radius: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>My GitHub Repositories</h1>
        <div class="stars-counter">
            <span class="emoji">⭐️</span> Total Stars: {total_stars}
        </div>
        <table>
            <tr>
                <th>Repository</th>
                <th>Description</th>
                <th>Freshness</th>
                <th>⭐️</th>
            </tr>
'''

    markdown_content = f'''
# My GitHub Repositories

**Total Stars: {total_stars}**

| Repository | Description | Freshness | ⭐️ |
|------------|-------------|-----------|----|
'''

    for repo in repositories:
        repo_name = repo['name']
        repo_url = repo['html_url']
        repo_description = repo['description'] or "No description"
        latest_commit_date = fetch_latest_commit_date(repo_name)
        stars_count = repo['stargazers_count']

        if latest_commit_date:
            humanized_commit_date = humanize_commit_date(latest_commit_date)
        else:
            humanized_commit_date = 'N/A'

        html_content += f'''
            <tr>
                <td><a href="{repo_url}" target="_blank">{repo_name}</a></td>
                <td class="description">{repo_description}</td>
                <td>
                    <img src="https://img.shields.io/github/last-commit/{GITHUB_USERNAME}/{repo_name}?style=flat-square" alt="Last Commit"> 
                </td>
                <td>
                    <img src="https://img.shields.io/github/stars/{GITHUB_USERNAME}/{repo_name}?style=flat-square" alt="Stars"> 
                </td>
            </tr>
'''

        markdown_content += f'| [{repo_name}]({repo_url}) | {repo_description} | ![Last Commit](https://img.shields.io/github/last-commit/{GITHUB_USERNAME}/{repo_name}?style=flat-square) | ![Stars](https://img.shields.io/github/stars/{GITHUB_USERNAME}/{repo_name}?style=flat-square) |\n'

    html_content += '''
        </table>
    </div>
</body>
</html>
'''

    markdown_content += '''
'''

    with open('docs/index.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)

    print('GitHub repositories HTML page and README.md generated')

def main():
    repositories = fetch_repositories_with_stars(min_stars=5)
    generate_html_page(repositories)

if __name__ == '__main__':
    main()
