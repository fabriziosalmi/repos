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
            time.sleep(0.2) # Rate limiting

        except requests.exceptions.RequestException as e:
            console.print(f"  [yellow]Warning: Could not retrieve issues for {repo_url}: {e}[/yellow]")
            return None

    if closed_issue_count > 0:
        return total_resolution_time / closed_issue_count
    else:
        return 0


def get_starred_repositories(username, token=None, console=None):
    """Fetches starred repos, calculates stats (including 1-month star increment)."""
    if console is None:
        console = Console()

    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'

    starred_repos = []
    total_stars = 0
    page = 1
    per_page = 100
    all_repo_names = [] # for star chart

    try:
        while True:
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
            retry_count = 0
            max_retries = 5
            while retry_count < max_retries:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if isinstance(e, requests.exceptions.HTTPError) and response.status_code == 403:
                        if "Retry-After" in response.headers:
                            retry_after = int(response.headers["Retry-After"])
                            console.print(f"[yellow]Secondary Rate Limit. Waiting {retry_after}s.[/yellow]")
                            time.sleep(retry_after)
                            continue

                    retry_count += 1
                    wait_time = 2 ** retry_count
                    console.print(f"[yellow]Request failed (page {page}, attempt {retry_count}/{max_retries}): {e}. Retrying in {wait_time}s.[/yellow]")
                    time.sleep(wait_time)

            if retry_count == max_retries:
                console.print(f"[red]Failed to fetch repository list (page {page}) after retries.[/red]")
                return None, None, []  # Return empty list for repo names

            repos = response.json()
            if not repos:
                break

            for repo in track(repos, description=f"Processing repositories (page {page})...", console=console, transient=True):
                if repo.get('stargazers_count', 0) > 0:
                    try:
                        # --- Commit, Contributors ---
                        commits_url = repo['commits_url'].replace('{/sha}', '')
                        commits_response = requests.get(commits_url, headers=headers, params={'per_page': 1}, timeout=5)
                        commits_response.raise_for_status()
                        if 'Link' in commits_response.headers:
                            last_page_link = commits_response.headers['Link'].split(',')[-1]
                            commit_count = int(last_page_link.split('>; rel="last"')[0].split('page=')[-1])
                        elif commits_response.status_code == 200:
                            commit_count = len(commits_response.json())
                        else:
                            commit_count = 0
                            console.print(f"[yellow]Warning: Could not retrieve commit count for {repo['name']}: {commits_response.status_code}[/yellow]")

                        contributors_url = repo['contributors_url']
                        contributors_response = requests.get(contributors_url, headers=headers, params={'per_page': 1, 'anon': 'true'}, timeout=5)
                        contributors_response.raise_for_status()
                        if 'Link' in contributors_response.headers:
                            last_page_link = contributors_response.headers['Link'].split(',')[-1]
                            contributors_count = int(last_page_link.split('>; rel="last"')[0].split('page=')[-1])
                        elif contributors_response.status_code == 200:
                            contributors_count = len(contributors_response.json())
                        else:
                            contributors_count = 0
                            console.print(f"[yellow]Warning: Could not retrieve contributors count for {repo['name']}: {contributors_response.status_code}[/yellow]")

                        # --- Last Update ---
                        updated_at_str = repo.get('updated_at')
                        created_at_str = repo.get('created_at')
                        if updated_at_str and created_at_str:
                            updated_at = datetime.datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                            created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            last_update = get_human_readable_time(updated_at)
                        else:
                            last_update = "Unknown"
                            console.print(f"[yellow]Warning: Missing update/creation date for {repo.get('name', 'Unknown')}[/yellow]")

                        # --- 1-Month Star Increment ---
                        one_month_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(weeks=4)
                        stars_one_month_ago = 0

                        if created_at <= one_month_ago:
                          stargazers_url = repo['stargazers_url'] + "?per_page=100"
                          stargazers_page = 1
                          while True:
                              try:
                                  stargazers_response = requests.get(stargazers_url + f"&page={stargazers_page}", headers=headers, timeout=5)
                                  stargazers_response.raise_for_status()
                                  stargazers = stargazers_response.json()

                                  if not stargazers:
                                      break

                                  last_stargazer = stargazers[-1]
                                  last_starred_at_str = last_stargazer.get("starred_at")

                                  if last_starred_at_str:
                                    last_starred_at = datetime.datetime.fromisoformat(last_starred_at_str.replace('Z', '+00:00'))
                                    if last_starred_at <= one_month_ago:
                                        stars_one_month_ago += len(stargazers)
                                        break

                                  stars_one_month_ago += len(stargazers)

                                  if 'next' not in stargazers_response.links:
                                    break

                                  stargazers_page += 1
                                  time.sleep(0.1)

                              except requests.exceptions.RequestException as e:
                                  console.print(f"[yellow]Warning: Could not retrieve stargazers for {repo['name']}: {e}[/yellow]")
                                  stars_one_month_ago = 0
                                  break

                        current_stars = repo.get('stargazers_count', 0)
                        star_increment_month = current_stars - stars_one_month_ago
                        total_stars += current_stars

                        # --- Average Issue Resolution Time ---
                        avg_resolution_time = get_average_issue_resolution_time(repo['html_url'], headers, console)

                        # --- Get the number of closed issues ---
                        issues_count = 0
                        if avg_resolution_time is not None:
                            issues_url = repo['html_url'].replace("https://github.com/", "https://api.github.com/repos/") + "/issues?state=closed"
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

                        repo_info = {
                            'url': repo.get('html_url', 'N/A'),
                            'name': repo.get('name', 'N/A'),
                            'description': repo.get('description', "No description"),
                            'stars': current_stars,
                            'commit_count': commit_count,
                            'contributors_count': contributors_count,
                            'last_update': updated_at.isoformat(),  # Convert to ISO format string
                            'last_update_str': last_update,
                            'avg_issue_resolution_time': avg_resolution_time,
                            'issues_count': issues_count,
                            'star_increment_month': star_increment_month,
                        }
                        starred_repos.append(repo_info)
                        all_repo_names.append(repo.get('full_name')) # add to list

                    except requests.exceptions.RequestException as e:
                        console.print(f"  [yellow]Warning: Skipping repository {repo.get('name', 'Unknown')} due to error:[/yellow] {e}")
                        continue

            page += 1
            time.sleep(0.5)

    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {e}")
        return None, None, []  # Return empty list for repo names

    # Sort the repositories
    starred_repos.sort(key=lambda repo: (
        repo['stars'],
        datetime.datetime.fromisoformat(repo['last_update']), # convert back to datetime for sort
        repo['avg_issue_resolution_time'] if repo['avg_issue_resolution_time'] is not None else float('inf'),
        repo['issues_count'],
        repo['name'].lower()
    ), reverse=True)
    starred_repos.sort(key=lambda x: x['avg_issue_resolution_time'] if x['avg_issue_resolution_time'] is not None else float('inf'))

    return starred_repos, total_stars, all_repo_names # return also names

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

def create_markdown_table(repositories, total_stars, repo_names, filename="stats.md"):
    """Creates a Markdown table and includes the star history chart."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Starred Repositories\n\n")
            f.write(f"**Total Stars:** {total_stars}\n\n")

            # Create the star history chart URL
            repo_list = ",".join(repo_names)
            chart_url = f"https://api.star-history.com/svg?repos={repo_list}&type=Date&theme=dark"
            f.write(f"![Star History Chart]({chart_url})\n\n")  # Embed the chart

            f.write("| Repository | URL | Description | Stars | +1 Month | Commits | Contributors | Last Update | Avg. Issue Resolution |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")

            for repo in repositories:
                description = repo['description'].replace("|", "\\|").replace("\n", "<br>")
                stars_emoji = "⭐" if repo['stars'] > 0 else ""
                if repo['stars'] >= 100:
                    stars_emoji = "🌟"
                if repo['stars'] >= 500:
                    stars_emoji = "✨"

                commit_emoji = "📝"
                if repo['commit_count'] >= 100:
                    commit_emoji = "🔥🔥"
                if repo['commit_count'] >= 1000:
                    commit_emoji = "💥💥💥"

                contributors_emoji = "🧑‍💻"
                if repo['contributors_count'] > 5:
                    contributors_emoji = "🧑‍💻🧑‍💻"
                if repo['contributors_count'] > 50:
                    contributors_emoji = "🧑‍💻🧑‍💻🧑‍💻"

                resolution_time_str = format_resolution_time(repo['avg_issue_resolution_time'])
                star_increment_str = f"+{repo['star_increment_month']}" if repo['star_increment_month'] > 0 else str(repo['star_increment_month'])

                f.write(f"| **{repo['name']}** | [{repo['url']}]({repo['url']}) | {description} | {stars_emoji} {repo['stars']} | {star_increment_str} | {commit_emoji} {repo['commit_count']} | {contributors_emoji} {repo['contributors_count']} | {repo['last_update_str']} | {resolution_time_str} |\n")

        print(f"Markdown table saved to {filename}")

    except Exception as e:
        print(f"Error creating Markdown table: {e}")

if __name__ == '__main__':
    username = 'fabriziosalmi'
    github_token = os.environ.get('GITHUB_TOKEN')

    custom_theme = Theme({
        "repo_name": "bold cyan",
        "url": "blue",
        "description": "italic green",
        "stars": "yellow",
        "commits": "magenta",
        "contributors": "bright_red",
        "last_update": "bright_white",
        "header": "bold white on blue",
        "total_stars": "bold yellow",
        "avg_resolution": "bold green",
        "star_increment": "bold blue",
    })
    console = Console(theme=custom_theme)

    starred_repositories, total_stars, all_repo_names = get_starred_repositories(username, github_token, console)

    if starred_repositories:
        # --- Display Table (Rich) ---
        table = Table(title=f"Starred Repositories for {username}", show_header=True, header_style="header")
        table.add_column("Repository", style="repo_name", min_width=20)
        table.add_column("URL", style="url", max_width=50)
        table.add_column("Description", style="description", max_width=40)
        table.add_column("Stars", style="stars", justify="right")
        table.add_column("1 Month Incr.", style="star_increment", justify="right")
        table.add_column("Commits", style="commits", justify="right")
        table.add_column("Contributors", style="contributors", justify="right")
        table.add_column("Last Update", style="last_update", justify="right")
        table.add_column("Avg. Issue Resolution", style="avg_resolution", justify="right")

        for repo in starred_repositories:
            resolution_time_str = format_resolution_time(repo['avg_issue_resolution_time'])
            star_increment_str = f"+{repo['star_increment_month']}" if repo['star_increment_month'] > 0 else str(repo['star_increment_month'])
            table.add_row(
                repo['name'],
                repo['url'],
                repo['description'],
                str(repo['stars']),
                star_increment_str,
                str(repo['commit_count']),
                str(repo['contributors_count']),
                repo['last_update_str'],  # Use human-readable string here
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
        create_markdown_table(starred_repositories, total_stars, all_repo_names) # Pass repo names

    else:
        console.print(f"[yellow]No starred repositories found for {username} or an error occurred.[/yellow]")