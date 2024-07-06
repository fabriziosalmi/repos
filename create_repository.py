import os
import yaml
import requests
from bs4 import BeautifulSoup

GITHUB_USERNAME = 'your_github_username'

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
        <h1>My GitHub Repositories</h1>
    '''
    
    for repo in repositories:
        repo_name = repo.get('name')
        repo_description = repo.get('description')
        
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
    
    with open('github_repositories.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print('GitHub repositories HTML page generated: github_repositories.html')

def main():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        repositories = config.get('repositories', [])

        generate_html_page(repositories)

if __name__ == '__main__':
    main()
