import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Tuple
from tqdm import tqdm  # Import tqdm for the progress bar
import argparse  # Import argparse


def get_all_repositories(username: str, github_token: str) -> List[str]:
    """Fetches all public repositories for a given GitHub username."""
    repositories = []
    page = 1
    per_page = 100

    while True:
        headers = {"Authorization": f"token {github_token}"}
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            repos_data = response.json()
            if not repos_data:
                break
            for repo in repos_data:
                repositories.append(repo['full_name'])
            page += 1
        elif response.status_code == 403 and "rate limit" in response.text.lower():
            print("Error: Rate limit exceeded.  Please wait and try again later.")
            return []
        elif response.status_code == 404:
            print(f"Error: User '{username}' not found.")
            return []
        else:
            print(f"Error fetching repositories: {response.status_code} - {response.text}")
            return []
    return repositories


def get_stargazer_history(repo_full_name: str, github_token: str) -> List[Tuple[str, int]]:
    """Fetches the historical star count for a single repository."""
    stargazer_data = []
    page = 1
    per_page = 100

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3.star+json"
    }

    while True:
        url = f"https://api.github.com/repos/{repo_full_name}/stargazers?page={page}&per_page={per_page}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            stars_page = response.json()
            if not stars_page:
                break

            for star_info in stars_page:
                stargazer_data.append((star_info['starred_at'], 0))

            if 'next' not in response.links:
                break
            page += 1
        elif response.status_code == 403 and "rate limit" in response.text.lower():
            print("Error: Rate limit exceeded. Please wait or use a token.")
            return []
        else:
            print(f"Error fetching stargazers for {repo_full_name}: {response.status_code} - {response.text}")
            return []

    stargazer_data.sort()
    cumulative_count = 0
    history = []
    for date_str, _ in stargazer_data:
        cumulative_count += 1
        history.append((date_str, cumulative_count))

    return history


def aggregate_star_history(all_repos_history: List[List[Tuple[str, int]]], start_year: int) -> Dict[str, int]:
    """Aggregates star history, filtering by start year."""
    aggregated_history: Dict[str, int] = {}

    for repo_history in all_repos_history:
        for date_str, star_count in repo_history:
            date_only = date_str.split('T')[0]
            year = int(date_only.split('-')[0])
            if year >= start_year:  # Apply the start_year filter
                aggregated_history[date_only] = aggregated_history.get(date_only, 0) + 1

    return aggregated_history


def plot_star_history(aggregated_history: Dict[str, int], username: str, start_year: int):
    """Plots the aggregated star history."""
    dates = [datetime.fromisoformat(date) for date in aggregated_history.keys()]
    dates.sort()

    star_counts = []
    cumulative_stars = 0
    sorted_aggregated_history = dict(sorted(aggregated_history.items()))
    for stars_of_the_day in sorted_aggregated_history.values():
        cumulative_stars += stars_of_the_day
        star_counts.append(cumulative_stars)

    plt.figure(figsize=(12, 6))
    plt.plot(dates, star_counts)
    plt.xlabel("Date")
    plt.ylabel("Total Star Count")
    plt.title(f"GitHub Star History for {username} (Starting from {start_year})")  # Update title
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(f"github_star_history_{username}_{start_year}.png")  # Include start_year in filename
    print(f"Star history graph saved as github_star_history_{username}_{start_year}.png")
    plt.show()


def main():
    """Main function to get and plot GitHub star history."""

    parser = argparse.ArgumentParser(description="Generate a GitHub star history graph.")
    parser.add_argument("username", help="Your GitHub username")
    parser.add_argument("-t", "--token", help="Your GitHub Personal Access Token (optional, but recommended)", default=os.environ.get('GITHUB_TOKEN'))
    parser.add_argument("-s", "--start_year", type=int, default=2013, help="The starting year for the graph (default: 2008)")  # Add start_year argument
    args = parser.parse_args()

    username = args.username
    github_token = args.token
    start_year = args.start_year

    if not username:
        print("Error: GitHub username is required.")
        return

    # Validate start_year
    current_year = datetime.now().year
    if start_year < 2008 or start_year > current_year: # GitHub was founded in 2008
        print(f"Error: start_year must be between 2008 and {current_year}.")
        return

    all_repos = get_all_repositories(username, github_token)
    if not all_repos:
        return

    all_repos_history = []
    for repo in tqdm(all_repos, desc="Fetching stargazer history"):
        repo_history = get_stargazer_history(repo, github_token)
        if repo_history:
            all_repos_history.append(repo_history)

    aggregated_history = aggregate_star_history(all_repos_history, start_year)  # Pass start_year
    plot_star_history(aggregated_history, username, start_year)  # Pass start_year


if __name__ == "__main__":
    main()