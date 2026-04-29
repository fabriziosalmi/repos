# -*- coding: utf-8 -*-
"""GitHub repository stats orchestrator.

Aggregates owned repos for a given user via the GitHub API and writes
`public_data/repositories-data.json`. Library modules under `lib/` hold the
HTTP client, cache, per-repo metric fetchers, advanced signals, and output
writers; this file wires them together and exposes the top-level CLI.
"""

import json
import logging
import os
import sys
import time

from rich.console import Console
from rich.progress import track

from lib.advanced_metrics import (
    calculate_bus_factor,
    calculate_issue_health,
    calculate_momentum_score,
    fetch_recent_commits,
    fetch_top_contributors,
)
from lib.cache import CACHE_DURATION_HOURS, CACHE_FILE, load_cache, save_cache
from lib.github_api import (
    DEFAULT_PAGE_SIZE,
    GITHUB_API_BASE_URL,
    INITIAL_RETRY_DELAY,
    MAX_RETRIES,
    MAX_RETRY_DELAY,
    REQUEST_TIMEOUT,
    get_count_from_link_header,
    make_github_request,
)
from lib.output import create_markdown_table, save_to_json
from lib.repo_metrics import (
    get_average_issue_resolution_time,
    get_latest_version_info,
    get_repository_languages,
)
from lib.utils import (
    format_resolution_time,
    generate_repository_insights,
    get_human_readable_time,
    get_repository_status_indicator,
    parse_github_datetime,
    safe_file_write,
    validate_data_completeness,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Re-exports for backward compatibility (test_stats.py imports from `stats`)
__all__ = [
    'CACHE_FILE', 'CACHE_DURATION_HOURS', 'load_cache', 'save_cache',
    'GITHUB_API_BASE_URL', 'REQUEST_TIMEOUT', 'DEFAULT_PAGE_SIZE',
    'MAX_RETRIES', 'INITIAL_RETRY_DELAY', 'MAX_RETRY_DELAY',
    'make_github_request', 'get_count_from_link_header',
    'validate_data_completeness', 'safe_file_write', 'get_human_readable_time',
    'parse_github_datetime', 'format_resolution_time',
    'get_repository_status_indicator', 'generate_repository_insights',
    'get_average_issue_resolution_time', 'get_repository_languages',
    'get_latest_version_info',
    'calculate_momentum_score', 'calculate_issue_health', 'calculate_bus_factor',
    'fetch_recent_commits', 'fetch_top_contributors',
    'save_to_json', 'create_markdown_table',
    'get_user_repositories_stats', 'main',
]


def get_user_repositories_stats(username, token=None, console=None):
    """Fetch owned repos for a user, calculate stats, and sort by stars."""
    if console is None:
        console = Console()

    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        logging.info(f"Using provided GitHub token for user {username}.")
    else:
        logging.warning(f"No GitHub token provided for user {username}. Rate limits will be stricter.")

    repo_data = {}
    total_stars = 0
    page = 1
    all_repo_names = []

    logging.info(f"Fetching repository list for user {username}...")
    try:
        while True:
            url = f"{GITHUB_API_BASE_URL}/users/{username}/repos"
            params = {'page': page, 'per_page': DEFAULT_PAGE_SIZE, 'type': 'owner', 'sort': 'full_name'}
            response = make_github_request(url, headers, params=params, console=console)

            if response is None:
                console.print(f"[red]Failed to fetch repository list (page {page}) for {username} after multiple retries. Aborting.[/red]")
                return None, None, []

            try:
                repos = response.json()
                if not isinstance(repos, list):
                    logging.error(f"Unexpected JSON response type for repo list (page {page}): {type(repos)}")
                    console.print(f"[red]Unexpected data format received for repository list (page {page}). Aborting.[/red]")
                    return None, None, []
            except json.JSONDecodeError:
                console.print(f"[red]Failed to decode JSON for repository list (page {page}). Aborting.[/red]")
                return None, None, []

            if not repos:
                logging.info(f"No more repositories found for {username} on page {page}.")
                break

            logging.info(f"Processing page {page} of repositories ({len(repos)} found).")
            page_repo_names = []
            for repo in track(repos, description=f"Processing basic repo info (page {page})...", console=console, transient=True):
                if not isinstance(repo, dict):
                    logging.warning(f"Skipping invalid item in repository list: {type(repo)}")
                    continue

                full_name = repo.get('full_name')
                if not full_name:
                    logging.warning(f"Skipping repository with missing 'full_name': {repo.get('name')}")
                    continue

                repo_data[full_name] = {
                    'url': repo.get('html_url', '#'),
                    'name': repo.get('name', 'N/A'),
                    'full_name': full_name,
                    'description': repo.get('description') or "No description",
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'watchers': repo.get('watchers_count', 0),
                    'language': repo.get('language', 'Not specified'),
                    'archived': repo.get('archived', False),
                    'disabled': repo.get('disabled', False),
                    'private': repo.get('private', False),
                    'fork': repo.get('fork', False),
                    'license': repo.get('license', {}).get('name') if repo.get('license') else 'No license',
                    'default_branch': repo.get('default_branch', 'main'),
                    'open_issues_count': repo.get('open_issues_count', 0),
                    'size': repo.get('size', 0),
                    'last_update': parse_github_datetime(repo.get('pushed_at') or repo.get('updated_at')),
                    'created_at_api': parse_github_datetime(repo.get('created_at')),
                    'has_issues': repo.get('has_issues', False),
                    'commits': None,
                    'contributors': None,
                    'last_update_str': "Fetching...",
                    'avg_issue_resolution_time': None,
                    'closed_issues_count': None,
                    'processed_details': False
                }
                page_repo_names.append(full_name)
                total_stars += repo_data[full_name]['stars']

            all_repo_names.extend(page_repo_names)

            if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
                page += 1
                time.sleep(0.2)
            else:
                break

        logging.info(f"Fetched basic info for {len(all_repo_names)} repositories. Total stars: {total_stars:,}.")
        logging.info("Fetching detailed information for each repository...")

        repo_keys_to_process = list(repo_data.keys())
        for full_name in track(repo_keys_to_process, description="Fetching detailed info", console=console):
            if full_name not in repo_data:
                logging.warning(f"Full name '{full_name}' from key list not found in repo_data dict. Skipping.")
                continue
            repo_info = repo_data[full_name]
            repo_api_url_base = f"{GITHUB_API_BASE_URL}/repos/{full_name}"

            if repo_info['processed_details']:
                continue

            try:
                # --- Commit count (Link-header trick with per_page=1) ---
                commits_url = f"{repo_api_url_base}/commits"
                commits_response_count = make_github_request(commits_url, headers, params={'per_page': 1}, console=console)
                commit_count = None

                if commits_response_count:
                    link_count = get_count_from_link_header(commits_response_count)
                    if link_count is not None:
                        commit_count = link_count
                    elif commits_response_count.status_code == 200:
                        try:
                            commits_json = commits_response_count.json()
                            commit_count = len(commits_json) if isinstance(commits_json, list) else 0
                        except (json.JSONDecodeError, TypeError):
                            logging.warning(f"Could not decode commits JSON for {full_name} when Link header was missing.")
                            commit_count = 0
                    elif commits_response_count.status_code == 409:
                        logging.info(f"Repository {full_name} is empty (409 conflict on commits). Setting commit count to 0.")
                        commit_count = 0
                    else:
                        logging.warning(f"Could not determine commit count for {full_name} via Link header. Status: {commits_response_count.status_code}")
                        commit_count = 0
                else:
                    logging.warning(f"Failed request for commit count link header for {full_name}.")

                repo_info['commits'] = commit_count

                # --- Contributors count ---
                contributors_url = f"{repo_api_url_base}/contributors"
                contrib_response = make_github_request(contributors_url, headers, params={'per_page': 1, 'anon': 'true'}, console=console)
                contributors_count = None

                if contrib_response:
                    link_count = get_count_from_link_header(contrib_response)
                    if link_count is not None:
                        contributors_count = link_count
                    elif contrib_response.status_code == 200:
                        try:
                            contributors_json = contrib_response.json()
                            contributors_count = len(contributors_json) if isinstance(contributors_json, list) else 0
                        except (json.JSONDecodeError, TypeError):
                            logging.warning(f"Could not decode contributors JSON for {full_name} when Link header was missing.")
                            contributors_count = 0
                    elif contrib_response.status_code == 204:
                        logging.info(f"Repo {full_name} reported 204 No Content for contributors (may still be processing). Setting count to 0 for now.")
                        contributors_count = 0
                    else:
                        logging.warning(f"Could not determine contributor count for {full_name}. Status: {contrib_response.status_code}")
                        contributors_count = 0
                else:
                    logging.warning(f"Failed request for contributor count for {full_name}.")

                repo_info['contributors'] = contributors_count

                # --- Last update string ---
                if repo_info['last_update']:
                    repo_info['last_update_str'] = get_human_readable_time(repo_info['last_update'])
                else:
                    repo_info['last_update_str'] = "Unknown"

                # --- Average issue resolution time ---
                has_issues = repo_info.get('has_issues', True)
                avg_res_time_secs = None

                if has_issues:
                    avg_res_time_secs = get_average_issue_resolution_time(full_name, headers, console)
                else:
                    logging.info(f"Skipping issue resolution calculation for {full_name} as issues are disabled.")
                    avg_res_time_secs = 0.0

                repo_info['avg_issue_resolution_time'] = avg_res_time_secs

                # --- Closed issue count ---
                closed_issues_count = None

                if has_issues:
                    issues_url = f"{repo_api_url_base}/issues"
                    issues_response = make_github_request(issues_url, headers, params={'state': 'closed', 'per_page': 1}, console=console)
                    if issues_response:
                        link_count = get_count_from_link_header(issues_response)
                        if link_count is not None:
                            closed_issues_count = link_count
                        elif issues_response.status_code == 200:
                            try:
                                issues_json = issues_response.json()
                                closed_issues_count = len(issues_json) if isinstance(issues_json, list) else 0
                            except (json.JSONDecodeError, TypeError):
                                logging.warning(f"Could not decode issues JSON for {full_name} when Link header was missing.")
                                closed_issues_count = 0
                        else:
                            logging.warning(f"Could not determine closed issue count for {full_name}. Status: {issues_response.status_code}")
                            closed_issues_count = 0
                    else:
                        logging.warning(f"Failed request for closed issue count for {full_name}.")
                else:
                    closed_issues_count = 0

                repo_info['closed_issues_count'] = closed_issues_count

                # --- Language statistics (skip archived/disabled) ---
                if not repo_info.get('archived', False) and not repo_info.get('disabled', False):
                    language_stats = get_repository_languages(full_name, headers, console)
                    repo_info['language_stats'] = language_stats

                    if language_stats:
                        primary_language = list(language_stats.keys())[0]
                        repo_info['language'] = primary_language
                else:
                    repo_info['language_stats'] = {}

                # --- Latest version (release/tag) ---
                version_info = get_latest_version_info(full_name, headers, console)
                repo_info['version'] = version_info.get('name')

                repo_info['status'] = get_repository_status_indicator(repo_info)

                # --- Advanced metrics ---
                momentum = calculate_momentum_score(
                    full_name, repo_info.get('stars', 0), headers, console
                )
                repo_info['momentum'] = momentum

                issue_health = calculate_issue_health(
                    full_name,
                    repo_info.get('open_issues_count', 0),
                    repo_info.get('avg_issue_resolution_time'),
                    headers, console
                )
                repo_info['issue_health'] = issue_health

                bus_factor = calculate_bus_factor(repo_info.get('contributors'))
                repo_info['bus_factor'] = bus_factor

                logging.info(f"  Metrics for {full_name}: Momentum={momentum['score']}, Health={issue_health['health_score']}, BusFactor={bus_factor['bus_factor']}")

                repo_info['processed_details'] = True
                time.sleep(0.1)

            except Exception as e:
                logging.error(f"Unexpected error processing details for {full_name}: {e}", exc_info=True)
                console.print(f"  [red]Error processing details for {full_name}: {e}. Skipping details.[/red]")
                repo_info['processed_details'] = True
                continue

    except Exception as e:
        logging.error(f"An unexpected error occurred during repository fetching/processing: {e}", exc_info=True)
        console.print(f"[bold red]An critical error occurred: {e}[/]")
        return None, None, []

    processed_repos = list(repo_data.values())
    processed_repos.sort(key=lambda repo: repo.get('stars', 0) or 0, reverse=True)

    top_10_repos = processed_repos[:10]
    top_10_repo_full_names = [repo['full_name'] for repo in top_10_repos if repo.get('full_name')]

    logging.info("Finished processing all repositories.")
    return processed_repos, total_stars, top_10_repo_full_names


def main():
    """Main function with comprehensive error handling and validation."""
    start_time = time.time()
    console = Console()

    try:
        target_username = 'fabriziosalmi'
        github_token = os.environ.get('MY_PAT')
        output_dir = 'public_data'

        console.print(f"[info]Fetching repository statistics for user: [bold]{target_username}[/bold]...[/]")
        if not github_token:
            console.print("[warning]Environment variable 'MY_PAT' not set. Using unauthenticated requests (lower rate limits).[/warning]")
        else:
            console.print("[info]Using GitHub token from MY_PAT environment variable.[/info]")

        cached_data = load_cache()
        if cached_data:
            console.print("[info]Using cached data to avoid API rate limits.[/info]")
            user_repositories = cached_data.get('repositories', [])
        else:
            user_repositories, _, _ = get_user_repositories_stats(
                target_username, github_token, console
            )

            if user_repositories is not None:
                save_cache({'repositories': user_repositories})

        if user_repositories is not None:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            static_api_filename = os.path.join(output_dir, "repositories-data.json")

            def write_static_api():
                save_to_json(user_repositories, filename=static_api_filename)

            if not safe_file_write(static_api_filename, write_static_api):
                console.print(f"[error]Failed to write static API JSON file: {static_api_filename}[/error]")
                return False

            console.print("[info]All files generated successfully.[/info]")
            return True

        console.print(f"[error]Could not retrieve repository data for {target_username}. Please check logs or username/token.[/error]")
        logging.error(f"Failed to retrieve repository data for {target_username}")
        return False

    except KeyboardInterrupt:
        console.print("[warning]Process interrupted by user.[/warning]")
        logging.info("Process interrupted by user")
        return False
    except Exception as e:
        console.print(f"[error]Critical error occurred: {e}[/error]")
        logging.error(f"Critical error in main function: {e}", exc_info=True)
        return False
    finally:
        end_time = time.time()
        console.print(f"[info]Script finished in {end_time - start_time:.2f} seconds.[/info]")


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('github_stats.log'),
            logging.StreamHandler()
        ]
    )

    success = main()
    if not success:
        logging.error("Script execution failed")
        sys.exit(1)
    logging.info("Script execution completed successfully")
    sys.exit(0)
