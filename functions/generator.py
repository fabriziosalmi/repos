from .fetcher import fetch_latest_commit_date
from .processor import humanize_commit_date, get_freshness_badge

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
            {total_stars} stargazers ❤️
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

{total_stars} stargazers ❤️

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

        freshness_badge_html = get_freshness_badge(humanized_commit_date)
        freshness_badge_md = get_freshness_badge(humanized_commit_date, for_markdown=True)

        html_content += f'''
            <tr>
                <td><a href="{repo_url}" target="_blank">{repo_name}</a></td>
                <td class="description">{repo_description}</td>
                <td>{freshness_badge_html}</td>
                <td>{stars_count}</td>
            </tr>
'''

        markdown_content += f'| [{repo_name}]({repo_url}) | {repo_description} | {freshness_badge_md} | {stars_count} |\n'

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
