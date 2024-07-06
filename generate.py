import os
import requests
from bs4 import BeautifulSoup

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

    return repositories

def fetch_readme(repo_name):
    url = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/{repo_name}/main/README.md'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f'Failed to fetch README for {repo_name}. Status code: {response.status_code}')
            return None
    except requests.exceptions.RequestException as e:
        print(f'Error fetching README for {repo_name}: {e}')
        return None

def generate_html_page(repositories):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GitHub Repositories</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }
            .repo {
                margin-bottom: 40px;
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 8px;
            }
            h2 {
                color: #333;
            }
            .description {
                color: #666;
            }
        </style>
    </head>
    <body>
        <h1>My GitHub Repositories (with at least 5 stars)</h1>
    '''

    for repo in repositories:
        repo_name = repo['name']
        repo_description = repo['description']

        readme_content = fetch_readme(repo_name)
        if readme_content:
            soup = BeautifulSoup(readme_content, 'html.parser')
            readme_text = soup.get_text()
        else:
            readme_text = 'No README found.'

        html_content += f'''
        <div class="repo">
            <h2>{repo_name}</h2>
            <p class="description">{repo_description}</p>
            <p>{readme_text}</p>
        </div>
        '''

    html_content += '''
    </body>
    </html>
    '''

    # Ensure 'docs' folder exists
    if not os.path.exists('docs'):
        os.makedirs('docs')

    # Write HTML content to 'docs/github_repositories.html'
    with open('docs/github_repositories.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    print('GitHub repositories HTML page generated: docs/github_repositories.html')

def main():
    repositories = fetch_repositories_with_stars(min_stars=5)
    generate_html_page(repositories)

if __name__ == '__main__':
    main()
