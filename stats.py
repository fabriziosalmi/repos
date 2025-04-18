import os
import requests
import datetime
import time
import json
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.theme import Theme
from rich.markdown import Markdown
from rich.text import Text

def get_human_readable_time(timestamp):
    """Converts a timestamp to a human-readable time difference."""
    now = datetime.datetime.now(datetime.timezone.utc)
    time_diff = now - timestamp

    seconds = time_diff.total_seconds()
    days = time_diff.days

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30:
        return f"{int(days // 7)} weeks ago"
    elif days < 365:
        return f"{int(days // 30)} months ago"
    else:
        return f"{int(days // 365)} years ago"

def get_average_issue_resolution_time(repo_url, headers, console):
    """Calculates the average time to resolve issues for a single repository."""
    issues_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/issues?state=closed"
    total_resolution_time = 0
    closed_issue_count = 0
    page = 1

    while True:  # Paginate
        try:
            response = requests.get(issues_url + f"&page={page}&per_page=100", headers=headers, timeout=10)
            response.raise_for_status()
            issues = response.json()

            if not issues:
                break

            for issue in issues:
                if 'pull_request' not in issue:  # Only issues
                    created_at_str = issue.get('created_at')
                    closed_at_str = issue.get('closed_at')
                    if created_at_str is None or closed_at_str is None:
                        continue
                    created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    closed_at = datetime.datetime.fromisoformat(closed_at_str.replace('Z', '+00:00'))
                    resolution_time = (closed_at - created_at).total_seconds()
                    total_resolution_time += resolution_time
                    closed_issue_count += 1

            page += 1
            time.sleep(0.2)

        except requests.exceptions.RequestException as e:
            console.print(f"  [yellow]Warning: Could not retrieve issues for {repo_url}: {e}[/yellow]")
            return None

    if closed_issue_count > 0:
        return total_resolution_time / closed_issue_count
    else:
        return 0


def get_starred_repositories(username, token=None, console=None):
    """Fetches starred repos, calculates stats, and handles sorting."""
    if console is None:
        console = Console()

    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    starred_repos = []
    total_stars = 0
    page = 1
    per_page = 100
    all_repo_names = []
    repo_data = {}

    try:
        while True:
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
            retry_count = 0
            max_retries = 5
            while retry_count < max_retries:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

                    # Handle rate limiting explicitly using Retry-After header.
                    if response.status_code == 403 and "Retry-After" in response.headers:
                        retry_after = int(response.headers["Retry-After"])
                        console.print(f"[yellow]Secondary Rate Limit on repo list. Waiting {retry_after}s before retrying page {page}.[/yellow]")
                        time.sleep(retry_after)  # Wait the recommended time
                        continue # Retry the same request
                    break

                except requests.exceptions.RequestException as e:
                    console.print(f"[yellow]Request failed (page {page}, attempt {retry_count}/{max_retries}): {e}. Retrying in {2 ** retry_count}s.[/yellow]")
                    time.sleep(2 ** retry_count)  # Exponential backoff

            else:
                console.print(f"[red]Failed to fetch repository list (page {page}) after multiple retries.[/red]")
                return None, None, []

            repos = response.json()
            if not repos:
                break

            for repo in track(repos, description=f"Processing repositories (page {page})...", console=console, transient=True):
                if repo.get('stargazers_count', 0) > 0:
                    full_name = repo.get('full_name')
                    repo_data[full_name] = {
                        'url': repo.get('html_url', 'N/A'),
                        'name': repo.get('name', 'N/A'),
                        'description': repo.get('description', "No description"),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'commit_count': 0,
                        'contributors_count': 0,
                        'last_update': None,
                        'last_update_str': "Unknown",
                        'avg_issue_resolution_time': None,
                        'issues_count': 0,
                        'processed': False # Flag to indicate if detailed info is fetched
                    }

                    all_repo_names.append(full_name)
                    total_stars += repo_data[full_name]['stars']

            page += 1
            time.sleep(0.5)

        # ---  Process each repository to get detailed info. Ensure every repo is checked
        for full_name in track(all_repo_names, description="Fetching detailed info", console=console):
            if not repo_data[full_name]['processed']:
                try:
                    repo_info = repo_data[full_name] #access information

                    # --- Commit, Contributors ---
                    commits_url = f"https://api.github.com/repos/{full_name}/commits"
                    commits_response = None  # Initialize outside the try block
                    max_repo_retries = 5
                    for repo_retry in range(max_repo_retries):
                        try:
                            commits_response = requests.get(commits_url, headers=headers, params={'per_page': 1}, timeout=5)
                            commits_response.raise_for_status()
                            break  # Success, exit the retry loop
                        except requests.exceptions.RequestException as e:
                            console.print(f"  [yellow]Retrying commit count for {full_name} ({repo_retry+1}/{max_repo_retries}): {e}[/yellow]")
                            time.sleep(2 ** repo_retry)
                    else: # If all retries fail
                        console.print(f"[yellow]Failed to retrieve commit count for {full_name} after multiple retries.[/yellow]")
                        continue  # Skip to next repo after too many failures

                    if 'Link' in commits_response.headers:
                        last_page_link = commits_response.headers['Link'].split(',')[-1]
                        commit_count = int(last_page_link.split('>; rel="last"')[0].split('page=')[-1])
                    elif commits_response.status_code == 200:
                        commit_count = len(commits_response.json())
                    else:
                        commit_count = 0
                        console.print(f"[yellow]Warning: Could not retrieve commit count for {full_name}: {commits_response.status_code}[/yellow]")

                    repo_info['commit_count'] = commit_count

                    contributors_url = f"https://api.github.com/repos/{full_name}/contributors"
                    contributors_response = None  # Initialize outside the try block
                    for repo_retry in range(max_repo_retries):
                        try:
                            contributors_response = requests.get(contributors_url, headers=headers, params={'per_page': 1, 'anon': 'true'}, timeout=5)
                            contributors_response.raise_for_status()
                            break
                        except requests.exceptions.RequestException as e:
                            console.print(f"  [yellow]Retrying contributor count for {full_name} ({repo_retry+1}/{max_repo_retries}): {e}[/yellow]")
                            time.sleep(2 ** repo_retry)

                    else:
                        console.print(f"[yellow]Failed to retrieve contributor count for {full_name} after multiple retries.[/yellow]")
                        continue

                    if 'Link' in contributors_response.headers:
                        last_page_link = contributors_response.headers['Link'].split(',')[-1]
                        contributors_count = int(last_page_link.split('>; rel="last"')[0].split('page=')[-1])
                    elif contributors_response.status_code == 200:
                        contributors_count = len(contributors_response.json())
                    else:
                        contributors_count = 0
                        console.print(f"[yellow]Warning: Could not retrieve contributors count for {full_name}: {contributors_response.status_code}[/yellow]")

                    repo_info['contributors_count'] = contributors_count

                    # --- Last Update ---
                    repo_url = f"https://api.github.com/repos/{full_name}" # get more repo data
                    repo_response = requests.get(repo_url, headers=headers, timeout=10)
                    repo_response.raise_for_status()
                    repo_data_details = repo_response.json() # get details
                    updated_at_str = repo_data_details.get('updated_at')
                    created_at_str = repo_data_details.get('created_at')

                    if updated_at_str and created_at_str:
                        updated_at = datetime.datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                        created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        last_update = get_human_readable_time(updated_at)
                        repo_info['last_update'] = updated_at.isoformat()
                        repo_info['last_update_str'] = last_update
                    else:
                        repo_info['last_update_str'] = "Unknown"
                        console.print(f"[yellow]Warning: Missing update/creation date for {full_name}[/yellow]")

                    # --- Average Issue Resolution Time ---
                    avg_resolution_time = get_average_issue_resolution_time(repo_info['url'], headers, console) #use data

                    repo_info['avg_issue_resolution_time'] = avg_resolution_time

                    # --- Get the number of closed issues ---
                    issues_count = 0
                    if avg_resolution_time is not None:
                        issues_url = repo_info['url'].replace("https://github.com/", "https://api.github.com/repos/") + "/issues?state=closed"
                        try:
                            issues_response = requests.get(issues_url + "&page=1&per_page=1", headers=headers, timeout=5)
                            issues_response.raise_for_status()
                            if 'Link' in issues_response.headers:
                                last_page_link = issues_response.headers['Link'].split(',')[-1]
                                issues_count = int(last_page_link.split('>; rel="last"')[0].split('page=')[-1])
                            elif issues_response.status_code == 200:
                                issues_count = len(issues_response.json())
                        except requests.exceptions.RequestException:
                            pass

                    repo_info['issues_count'] = issues_count
                    repo_info['processed'] = True

                except requests.exceptions.RequestException as e:
                    console.print(f"  [yellow]Warning: General error processing {full_name}: {e}[/yellow]")
                    continue  # Process the next repo

    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {e}")
        return None, None, []

    # --- Sort the repositories after all info is gathered
    starred_repos = list(repo_data.values())
    starred_repos.sort(key=lambda repo: repo['stars'], reverse=True)

    # Get top 10 repos by stars for the chart
    top_10_repos = starred_repos[:10]
    top_10_repo_names = [repo['name'] for repo in top_10_repos]

    return starred_repos, total_stars, top_10_repo_names

def save_to_json(data, filename="stats.json"):
    """Saves the given data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def format_resolution_time(seconds):
    """Formats resolution time in a human-readable way."""
    if seconds is None:
        return "N/A"
    if seconds == 0:
        return "No Issues"
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_str = ""
    if days > 0:
        time_str += f"{int(days)}d "
    if hours > 0:
        time_str += f"{int(hours)}h "
    if minutes > 0:
        time_str += f"{int(minutes)}m "
    if seconds > 0:
        time_str += f"{int(seconds)}s"
    return time_str.strip()

def create_markdown_table(repositories, total_stars, repo_names, username, filename="stats.md"):
    """Creates a Markdown table with larger, consistent badges and star chart."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# My GitHub Repositories\n\n")
            f.write(f"{total_stars} stargazers ❤️\n\n")

            f.write(f"![fab's GitHub stats](https://github-readme-stats.vercel.app/api?username=fabriziosalmi)\n\n")

            # Star History Chart (Top 10)
            repo_list = ",".join([f"{username}/{name}" for name in repo_names])
            chart_url = f"https://api.star-history.com/svg?repos={repo_list}&type=Date&theme=dark"
            f.write(f"![Star History Chart]({chart_url})\n\n")

            f.write("| Repository | Description | Stars | Forks | Commits | Contributors | Issues | Last Update | Avg. Issue Resolution |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")

            for repo in repositories:
                description = repo['description'].replace("|", "\\|").replace("\n", "<br>")

                # Markdown table with normal text
                last_update_text = repo['last_update_str']

                resolution_time_str = format_resolution_time(repo['avg_issue_resolution_time'])

                f.write(f"| [{repo['name']}]({repo['url']}) | {description} | {repo['stars']} | {repo['forks']} | {repo['commit_count']} | {repo['contributors_count']} | {repo['issues_count']} | {last_update_text} | {resolution_time_str} |\n")
        print(f"Markdown table saved to {filename}")

    except Exception as e:
        print(f"Error creating Markdown table: {e}")

if __name__ == '__main__':
    username = 'fabriziosalmi'
    github_token = os.environ.get('MY_PAT')  # Get the PAT from environment variable

    custom_theme = Theme({
        "repo_name": "bold cyan",
        "description": "italic green",
        "stars": "yellow",
        "forks": "blue",
        "commits": "magenta",
        "contributors": "bright_red",
        "last_update": "bright_white",
        "header": "bold white on blue",
        "total_stars": "bold yellow",
        "avg_resolution": "bold green",
        "issues": "purple"
    })
    console = Console(theme=custom_theme)

    starred_repositories, total_stars, top_10_repo_names = get_starred_repositories(username, github_token, console)

    if starred_repositories:
        # --- Display Table (Rich) ---
        table = Table(title=f"Starred Repositories for {username}", show_header=True, header_style="header")
        table.add_column("Repository", style="repo_name", min_width=20)
        table.add_column("Description", style="description", max_width=50)
        table.add_column("Stars", style="stars", justify="right")
        table.add_column("Forks", style="forks", justify="right")
        table.add_column("Commits", style="commits", justify="right")
        table.add_column("Contributors", style="contributors", justify="right")
        table.add_column("Issues", style="issues", justify="right")
        table.add_column("Last Update", style="last_update", justify="right")
        table.add_column("Avg. Issue Resolution", style="avg_resolution", justify="right")

        for repo in starred_repositories:
            resolution_time_str = format_resolution_time(repo['avg_issue_resolution_time'])
            repo_link = Text.from_markup(f"[{repo['name']}]({repo['url']})")
            table.add_row(
                repo_link,
                repo['description'],
                str(repo['stars']),
                str(repo['forks']),
                str(repo['commit_count']),
                str(repo['contributors_count']),
                str(repo['issues_count']),
                repo['last_update_str'],
                resolution_time_str,
            )
        console.print(table)

        console.print(f"\n[total_stars]Total Stars Across All Repositories: {total_stars}[/]")

        # --- Save to JSON ---
        json_data = {
            'repositories': starred_repositories,
            'total_stars': total_stars,
        }
        save_to_json(json_data)

        # --- Create Markdown Table ---
        create_markdown_table(starred_repositories, total_stars, top_10_repo_names, username)

    else:
        console.print(f"[yellow]No starred repositories found for {username} or an error occurred.[/yellow]")
