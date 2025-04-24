import os
import requests
import datetime
import time
import json
# from collections import defaultdict # Not used, can be removed
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.theme import Theme
# from rich.markdown import Markdown # Not used, can be removed
from rich.text import Text
import logging # Added for better logging

# --- Configuration ---
# Configure logging for better debugging and information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Constants for API interaction
GITHUB_API_BASE_URL = "https://api.github.com"
REQUEST_TIMEOUT = 15 # Increased default timeout slightly
DEFAULT_PAGE_SIZE = 100
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 1 # seconds
MAX_RETRY_DELAY = 60 # seconds

# --- Helper Functions ---

def get_human_readable_time(timestamp):
    """Converts a timezone-aware datetime object to a human-readable time difference."""
    # Ensure timestamp is timezone-aware (expecting UTC from GitHub API)
    if timestamp.tzinfo is None:
        # This case should ideally not happen if parsing from ISO format with offset/Z
        logging.warning("Timestamp provided to get_human_readable_time is naive. Assuming UTC.")
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

    now = datetime.datetime.now(datetime.timezone.utc)
    # Ensure 'now' is also timezone-aware for correct comparison
    time_diff = now - timestamp

    seconds = time_diff.total_seconds()
    days = time_diff.days

    if seconds < 0:
        # Handle cases where timestamp might be slightly in the future due to clock skew
        return "just now"
    elif seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return f"{days} days ago"
    elif days < 30: # Using approx 30 days for a month
        return f"{int(days // 7)} weeks ago"
    elif days < 365:
        return f"{int(days // 30)} months ago" # Using approx 30 days/month
    else:
        return f"{int(days // 365)} years ago"

def parse_github_datetime(datetime_str):
    """Safely parses GitHub's ISO 8601 datetime strings."""
    if not datetime_str:
        return None
    try:
        # Handles the 'Z' for UTC directly
        return datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except (ValueError, TypeError) as e:
        logging.warning(f"Could not parse datetime string '{datetime_str}': {e}")
        return None

def make_github_request(url, headers, params=None, console=None, retries=MAX_RETRIES):
    """Makes a request to the GitHub API with error handling, rate limit awareness, and retries."""
    current_retry = 0
    delay = INITIAL_RETRY_DELAY
    while current_retry <= retries:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)

            # Check for rate limiting first
            if response.status_code == 403 and "Retry-After" in response.headers:
                retry_after = int(response.headers["Retry-After"])
                wait_time = max(retry_after, delay) # Wait at least the requested time
                logging.warning(f"Rate limit hit for {url}. Retrying after {wait_time} seconds.")
                if console:
                    console.print(f"[yellow]Rate limit hit. Waiting {wait_time}s...[/yellow]", end=" ")
                time.sleep(wait_time)
                if console:
                    console.print("[yellow]Resuming.[/yellow]")
                # Don't increment retry count for explicit rate limit waits requested by GitHub
                delay = INITIAL_RETRY_DELAY # Reset delay after successful wait
                continue # Retry the request

            response.raise_for_status() # Raise HTTPError for other bad responses (4xx or 5xx)
            return response # Success

        except requests.exceptions.Timeout as e:
            logging.warning(f"Request timed out for {url} (Attempt {current_retry+1}/{retries+1}): {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {url} (Attempt {current_retry+1}/{retries+1}): {e}")
            # Specific check for 404 Not Found - often means resource doesn't exist, retrying might not help
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                 logging.warning(f"Resource not found (404) at {url}. Aborting retries for this request.")
                 return None # Return None for 404

        # If caught an exception or non-rate-limit 403, prepare for retry
        current_retry += 1
        if current_retry <= retries:
            logging.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            delay = min(delay * 2, MAX_RETRY_DELAY) # Exponential backoff with cap
        else:
            logging.error(f"Max retries reached for {url}.")
            return None # Failed after all retries

    return None # Should not be reached, but included for safety

def get_count_from_link_header(response):
    """Extracts the total count of items from the Link header's 'last' relation."""
    if not response or 'Link' not in response.headers:
        return None
    link_header = response.headers['Link']
    links = link_header.split(',')
    for link in links:
        parts = link.split(';')
        if len(parts) == 2 and parts[1].strip() == 'rel="last"':
            try:
                last_url = parts[0].strip('<> ')
                # Extract the page number (more robust parsing)
                query_params = requests.utils.urlparse(last_url).query
                parsed_params = requests.compat.parse_qs(query_params)
                if 'page' in parsed_params:
                    return int(parsed_params['page'][0])
                # Fallback: simple split (less robust if URL structure changes)
                elif 'page=' in last_url:
                     return int(last_url.split('page=')[-1].split('&')[0])
            except (ValueError, IndexError) as e:
                logging.warning(f"Could not parse page number from 'last' link: {link}. Error: {e}")
                return None
    return None

def get_average_issue_resolution_time(repo_full_name, headers, console):
    """Calculates the average time to resolve issues for a single repository."""
    # Use repo_full_name directly
    issues_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/issues"
    total_resolution_seconds = 0
    closed_issue_count = 0
    page = 1

    logging.info(f"Calculating avg issue resolution time for {repo_full_name}...")

    while True:
        params = {'state': 'closed', 'page': page, 'per_page': DEFAULT_PAGE_SIZE}
        response = make_github_request(issues_url, headers, params=params, console=console)

        if response is None:
            logging.warning(f"Could not retrieve closed issues page {page} for {repo_full_name}. Stopping calculation.")
            # Return None if we failed to get any data, or partial data if we got some
            return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else None

        try:
            issues = response.json()
        except json.JSONDecodeError:
             logging.error(f"Failed to decode JSON response for closed issues of {repo_full_name}, page {page}.")
             # Decide how to handle: stop or try next page? Stopping is safer.
             return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else None


        if not issues:
            break # No more issues on this page or subsequent pages

        valid_issues_on_page = 0
        for issue in issues:
            # Ensure it's an issue and not a pull request, and has necessary dates
            if 'pull_request' not in issue and issue.get('created_at') and issue.get('closed_at'):
                created_at = parse_github_datetime(issue['created_at'])
                closed_at = parse_github_datetime(issue['closed_at'])

                if created_at and closed_at:
                    # Ensure closed_at is not before created_at
                    if closed_at >= created_at:
                        resolution_time = (closed_at - created_at).total_seconds()
                        total_resolution_seconds += resolution_time
                        closed_issue_count += 1
                        valid_issues_on_page += 1
                    else:
                        logging.warning(f"Issue {issue.get('number')} in {repo_full_name} closed before creation? Skipping.")
                else:
                     logging.warning(f"Could not parse dates for issue {issue.get('number')} in {repo_full_name}. Skipping.")

        logging.debug(f"Processed page {page} for {repo_full_name}, found {len(issues)} items, {valid_issues_on_page} valid closed issues.")

        # Check if there's a next page using Link header (more reliable than just checking list emptiness)
        if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
             page += 1
             time.sleep(0.1) # Small delay between pages
        else:
             break # No 'next' link found, assume this was the last page

    if closed_issue_count > 0:
        average_seconds = total_resolution_seconds / closed_issue_count
        logging.info(f"Calculated average resolution time for {repo_full_name}: {average_seconds:.2f} seconds over {closed_issue_count} issues.")
        return average_seconds
    else:
        logging.info(f"No valid closed issues found for {repo_full_name} to calculate average resolution time.")
        return 0 # Return 0 if no issues found, distinct from None (error)


# --- Renamed Function for Clarity ---
def get_user_repositories_stats(username, token=None, console=None):
    """Fetches owned repos for a user, calculates stats, and handles sorting."""
    if console is None:
        # Fallback console if none provided
        console = Console()

    headers = {'Accept': 'application/vnd.github.v3+json'} # Good practice to specify Accept header
    if token:
        headers['Authorization'] = f'token {token}'
        logging.info(f"Using provided GitHub token for user {username}.")
    else:
        logging.warning(f"No GitHub token provided for user {username}. Rate limits will be stricter.")

    repo_data = {}
    total_stars = 0
    page = 1
    all_repo_names = [] # Keep track of all repo full_names encountered

    logging.info(f"Fetching repository list for user {username}...")
    try:
        # --- Fetch initial list of repositories ---
        while True:
            url = f"{GITHUB_API_BASE_URL}/users/{username}/repos"
            params = {'page': page, 'per_page': DEFAULT_PAGE_SIZE, 'type': 'owner', 'sort': 'full_name'} # Explicitly request owned repos, sort for consistency
            response = make_github_request(url, headers, params=params, console=console)

            if response is None:
                console.print(f"[red]Failed to fetch repository list (page {page}) for {username} after multiple retries.[/red]")
                return None, None, [] # Return indicating failure

            try:
                repos = response.json()
            except json.JSONDecodeError:
                console.print(f"[red]Failed to decode JSON for repository list (page {page}).[/red]")
                return None, None, []

            if not repos:
                logging.info(f"No more repositories found for {username} on page {page}.")
                break # No more repositories

            logging.info(f"Processing page {page} of repositories ({len(repos)} found).")
            for repo in track(repos, description=f"Processing basic repo info (page {page})...", console=console, transient=True):
                full_name = repo.get('full_name')
                if not full_name:
                    logging.warning(f"Skipping repository with missing 'full_name': {repo.get('name')}")
                    continue

                # Store initial data, initialize detailed fields
                repo_data[full_name] = {
                    'url': repo.get('html_url', '#'), # Use '#' as fallback URL
                    'name': repo.get('name', 'N/A'),
                    'full_name': full_name, # Store full_name for later API calls
                    'description': repo.get('description') or "No description", # Ensure description is never None
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'last_update_api': parse_github_datetime(repo.get('updated_at')), # Store the datetime obj
                    'created_at_api': parse_github_datetime(repo.get('created_at')), # Store the datetime obj
                    # Initialize fields to be fetched later
                    'commit_count': None, # Use None to indicate not yet fetched or failed
                    'contributors_count': None,
                    'last_update_str': "Fetching...",
                    'avg_issue_resolution_time': None, # None indicates not calculated or error
                    'closed_issues_count': None, # Using closed_issues_count for clarity
                    'processed_details': False # Flag to indicate if detailed info fetch was attempted
                }
                all_repo_names.append(full_name)
                total_stars += repo_data[full_name]['stars']

            # Check for next page via Link header
            if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
                 page += 1
                 time.sleep(0.2) # Small delay between page requests
            else:
                 break # No 'next' link, assume last page


        logging.info(f"Fetched basic info for {len(all_repo_names)} repositories. Total stars: {total_stars}.")
        logging.info("Fetching detailed information for each repository...")

        # --- Process each repository to get detailed info ---
        # Using repo_data.keys() ensures we process based on what we initially stored
        for full_name in track(list(repo_data.keys()), description="Fetching detailed info", console=console):
            repo_info = repo_data[full_name]
            repo_api_url_base = f"{GITHUB_API_BASE_URL}/repos/{full_name}"

            try:
                # --- Commit Count ---
                commits_url = f"{repo_api_url_base}/commits"
                # Make a request for just one commit to potentially get the Link header
                commits_response = make_github_request(commits_url, headers, params={'per_page': 1}, console=console)
                commit_count = 0 # Default to 0
                if commits_response:
                    link_count = get_count_from_link_header(commits_response)
                    if link_count is not None:
                        commit_count = link_count * 1 # Get per_page from response? Assuming 1 for now. Need better logic if per_page!=1.
                        # The count from link header is the *last page number*. Total count is harder to get accurately this way if per_page > 1
                        # Let's refine this: fetch with per_page=1, check Link. If Link exists, parse last page number.
                        # If no link, count items in response (usually 1 if repo not empty).
                        # This is still an approximation for very large repos, the API doesn't easily give exact total commit count without pagination.
                        # A better approach might be needed if precision is critical (e.g. using GraphQL or paginating all commits).
                        # For now, let's stick to the Link header approach as an estimate.
                        # Let's re-evaluate the Link header logic:
                        # The 'last' link tells you the *number* of the last page.
                        # A more direct (but potentially slower for HUGE repos) way is to just paginate the commits endpoint.
                        # Alternative: Use the contributors endpoint, which often correlates but isn't the same.
                        # Let's stick to the Link header method but acknowledge its limitations.
                        # If Link header provides last page `N` with `per_page=1`, count is roughly `N`.
                        # Re-checking Github docs: The Search API might be better for counts, but has its own limits.
                        # Let's refine the logic for count based on response:
                        count_from_link = get_count_from_link_header(commits_response)
                        if count_from_link is not None:
                            # If last page is N, and per_page=1, count is N.
                            # Need confirmation if this is always true. Let's assume it's a reasonable estimate.
                            commit_count = count_from_link
                        else:
                            # If no Link header, it means only one page. Count items in JSON.
                            try:
                                commits_json = commits_response.json()
                                commit_count = len(commits_json)
                            except (json.JSONDecodeError, TypeError):
                                commit_count = 0 # Default if response invalid
                    elif commits_response.status_code == 200: # Check status just in case response exists but isn't 200
                         try:
                            commits_json = commits_response.json()
                            commit_count = len(commits_json) # Should be 1 or 0 if per_page=1
                         except (json.JSONDecodeError, TypeError):
                            commit_count = 0
                    else:
                         logging.warning(f"Could not determine commit count for {full_name}. Status: {commits_response.status_code}")
                         commit_count = 0
                else:
                    logging.warning(f"Failed request for commit count for {full_name}.")
                    commit_count = None # Indicate failure

                repo_info['commit_count'] = commit_count

                # --- Contributors Count ---
                contributors_url = f"{repo_api_url_base}/contributors"
                # Request with anon=true includes anonymous contributions in the count
                contrib_response = make_github_request(contributors_url, headers, params={'per_page': 1, 'anon': 'true'}, console=console)
                contributors_count = 0 # Default to 0
                if contrib_response:
                    count_from_link = get_count_from_link_header(contrib_response)
                    if count_from_link is not None:
                        contributors_count = count_from_link # Estimate based on last page number
                    elif contrib_response.status_code == 200:
                         try:
                            contributors_json = contrib_response.json()
                            contributors_count = len(contributors_json) # Count items on the single page
                         except (json.JSONDecodeError, TypeError):
                            contributors_count = 0
                    else:
                         logging.warning(f"Could not determine contributor count for {full_name}. Status: {contrib_response.status_code}")
                         contributors_count = 0
                else:
                    logging.warning(f"Failed request for contributor count for {full_name}.")
                    contributors_count = None # Indicate failure

                repo_info['contributors_count'] = contributors_count

                # --- Last Update String ---
                # Use the already fetched timestamp if available
                if repo_info['last_update_api']:
                    repo_info['last_update_str'] = get_human_readable_time(repo_info['last_update_api'])
                else:
                    # Fetching the repo details again just for updated_at is inefficient if list endpoint had it
                    # Let's rely on the initial fetch unless it was missing.
                    repo_info['last_update_str'] = "Unknown"
                    # Optionally, make another request if needed:
                    # repo_details_resp = make_github_request(repo_api_url_base, headers, console=console)
                    # if repo_details_resp:
                    #     repo_details_json = repo_details_resp.json()
                    #     updated_at_dt = parse_github_datetime(repo_details_json.get('updated_at'))
                    #     if updated_at_dt:
                    #         repo_info['last_update_api'] = updated_at_dt
                    #         repo_info['last_update_str'] = get_human_readable_time(updated_at_dt)


                # --- Average Issue Resolution Time ---
                # Pass full_name instead of potentially outdated URL from initial fetch
                avg_res_time_secs = get_average_issue_resolution_time(full_name, headers, console)
                repo_info['avg_issue_resolution_time'] = avg_res_time_secs # Can be float, 0, or None

                # --- Get the number of closed issues ---
                closed_issues_count = 0 # Default
                if avg_res_time_secs is not None: # Only try to get count if avg calc didn't fail completely
                    issues_url = f"{repo_api_url_base}/issues"
                    # Request just one issue to get Link header for count
                    issues_response = make_github_request(issues_url, headers, params={'state': 'closed', 'per_page': 1}, console=console)
                    if issues_response:
                        count_from_link = get_count_from_link_header(issues_response)
                        if count_from_link is not None:
                             closed_issues_count = count_from_link # Estimate from last page number
                        elif issues_response.status_code == 200:
                             try:
                                issues_json = issues_response.json()
                                closed_issues_count = len(issues_json) # Count items on single page
                             except (json.JSONDecodeError, TypeError):
                                closed_issues_count = 0
                        else:
                             logging.warning(f"Could not determine closed issue count for {full_name}. Status: {issues_response.status_code}")
                             closed_issues_count = 0
                    else:
                         logging.warning(f"Failed request for closed issue count for {full_name}.")
                         closed_issues_count = None # Indicate failure
                else:
                    closed_issues_count = None # Indicate error propagated from avg time calc

                repo_info['closed_issues_count'] = closed_issues_count
                repo_info['processed_details'] = True
                time.sleep(0.1) # Small delay between processing each repo's details

            except Exception as e:
                # Catch broader errors during processing of a single repo
                logging.error(f"Unexpected error processing details for {full_name}: {e}", exc_info=True)
                console.print(f"  [red]Error processing details for {full_name}: {e}. Skipping details.[/red]")
                # Mark as processed (attempted) but leave detailed fields as None/defaults
                repo_info['processed_details'] = True
                continue # Process the next repo

    except Exception as e:
        # Catch unexpected errors during the overall process
        logging.error(f"An unexpected error occurred during repository fetching/processing: {e}", exc_info=True)
        console.print(f"[bold red]An critical error occurred: {e}[/]")
        return None, None, []

    # --- Sort the repositories after all info is gathered ---
    # Convert repo_data dict values to a list
    processed_repos = list(repo_data.values())
    # Sort by stars descending
    processed_repos.sort(key=lambda repo: repo['stars'], reverse=True)

    # Get top 10 repo *names* for the chart URL (ensure they exist)
    top_10_repos = processed_repos[:10]
    top_10_repo_full_names = [repo['full_name'] for repo in top_10_repos if repo.get('full_name')]

    logging.info("Finished processing all repositories.")
    return processed_repos, total_stars, top_10_repo_full_names

def save_to_json(data, filename="github_stats.json"):
    """Saves the given data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Convert datetime objects to ISO strings for JSON compatibility
            def dt_converter(o):
                if isinstance(o, datetime.datetime):
                    return o.isoformat()
                return str(o) # Fallback for other types if needed

            json.dump(data, f, indent=4, default=dt_converter, ensure_ascii=False)
        logging.info(f"Data successfully saved to {filename}")
        print(f"Data saved to {filename}") # User feedback
    except (IOError, TypeError) as e:
        logging.error(f"Error saving data to JSON file '{filename}': {e}")
        print(f"Error saving to JSON: {e}") # User feedback

def format_resolution_time(seconds):
    """Formats resolution time in seconds into a human-readable string (d, h, m, s)."""
    if seconds is None:
        return "N/A" # Error or not calculated
    if seconds == 0:
        # Distinguish between zero time (unlikely but possible) and no closed issues
        # The calling function should ideally pass 0 only if there were no issues.
        return "No Closed Issues"
    if seconds < 0:
        logging.warning(f"Negative resolution time ({seconds}s) passed to formatter.")
        return "Invalid Data" # Should not happen

    # Ensure seconds is treated as float for precision before divmod
    seconds = float(seconds)

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, sec = divmod(remainder, 60) # Renamed to avoid shadowing

    parts = []
    if days >= 1:
        parts.append(f"{int(days)}d")
    if hours >= 1:
        parts.append(f"{int(hours)}h")
    if minutes >= 1:
        parts.append(f"{int(minutes)}m")
    if sec >= 1 or not parts: # Show seconds if > 1 or if it's the only unit (e.g., 0.5s)
        # Decide on precision for seconds
        if seconds < 60 and seconds != 0:
             parts.append(f"{sec:.1f}s") # Show decimal for small values
        elif sec >= 1:
             parts.append(f"{int(sec)}s")

    return " ".join(parts) if parts else "Instant" # If calculation resulted in zero seconds


def create_markdown_table(repositories, total_stars, top_repo_full_names, username, filename="github_stats.md"):
    """Creates a Markdown file with summary, chart, and detailed table."""
    logging.info(f"Generating Markdown report '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# GitHub Repository Stats for {username}\n\n")
            f.write(f"Total stars across all owned repositories: **{total_stars}** ⭐\n\n") # Use markdown bold

            # GitHub Readme Stats Card (Dynamic Username)
            f.write(f"## Overall Stats\n\n")
            f.write(f"![{username}'s GitHub stats](https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=radical)\n\n") # Added options

            # Star History Chart (Top N Repos)
            if top_repo_full_names:
                f.write(f"## Star History (Top {len(top_repo_full_names)} Repositories by Stars)\n\n")
                # URL encode repository names? Usually not necessary for star-history
                repo_list_param = ",".join(top_repo_full_names)
                # Use HTTPS for the chart URL
                chart_url = f"https://api.star-history.com/svg?repos={repo_list_param}&type=Date&theme=dark"
                f.write(f"![Star History Chart]({chart_url})\n\n")
            else:
                 f.write("*(Could not generate star history chart - no repositories found or an error occurred)*\n\n")

            # Detailed Repository Table
            f.write(f"## Repository Details\n\n")
            f.write("| Repository | Description | Stars ⭐ | Forks 🍴 | Commits  C | Contributors U | Closed Issues # | Last Update 🕒 | Avg. Issue Resolution ⏱️ |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")

            for repo in repositories:
                # Sanitize description for Markdown table cells
                description = repo.get('description', '')
                description = description.replace("|", "\\|") # Escape pipe characters
                description = description.replace("\n", "<br>") # Keep newlines visually

                # Format numbers and resolution time
                stars_str = f"{repo.get('stars', 0):,}"
                forks_str = f"{repo.get('forks', 0):,}"
                # Handle None for counts, indicate explicitly
                commits_str = f"{repo.get('commit_count', 0):,}" if repo.get('commit_count') is not None else "N/A"
                contrib_str = f"{repo.get('contributors_count', 0):,}" if repo.get('contributors_count') is not None else "N/A"
                issues_str = f"{repo.get('closed_issues_count', 0):,}" if repo.get('closed_issues_count') is not None else "N/A"
                last_update_str = repo.get('last_update_str', "Unknown")
                resolution_time_str = format_resolution_time(repo.get('avg_issue_resolution_time')) # Handles None/0

                f.write(f"| [{repo.get('name', 'N/A')}]({repo.get('url', '#')}) " # Link repo name
                        f"| {description} "
                        f"| {stars_str} "
                        f"| {forks_str} "
                        f"| {commits_str} "
                        f"| {contrib_str} "
                        f"| {issues_str} "
                        f"| {last_update_str} "
                        f"| {resolution_time_str} |\n")

        logging.info(f"Markdown report saved to {filename}")
        print(f"Markdown report saved to {filename}") # User feedback

    except IOError as e:
        logging.error(f"Error writing Markdown file '{filename}': {e}")
        print(f"Error creating Markdown file: {e}") # User feedback
    except Exception as e:
        logging.error(f"An unexpected error occurred during Markdown generation: {e}", exc_info=True)
        print(f"An unexpected error occurred creating Markdown file: {e}")

# --- Main Execution Block ---

if __name__ == '__main__':
    start_time = time.time()
    target_username = 'fabriziosalmi' # Or get from input/args
    github_token = os.environ.get('MY_PAT') # Get the PAT from environment variable

    # Configure Rich Console
    custom_theme = Theme({
        "repo_name": "bold cyan link", # Added link style implicitly via Text.from_markup
        "description": "dim", # Changed style
        "stars": "yellow",
        "forks": "blue",
        "commits": "magenta",
        "contributors": "green", # Changed color
        "issues": "purple",
        "last_update": "default", # Simpler style
        "header": "bold white on blue",
        "total_stars": "bold yellow",
        "avg_resolution": "bold green",
        "info": "dim cyan",
        "warning": "yellow",
        "error": "bold red",
    })
    console = Console(theme=custom_theme)

    console.print(f"[info]Fetching repository statistics for user: [bold]{target_username}[/bold]...[/]")
    if not github_token:
        console.print("[warning]Environment variable 'MY_PAT' not set. Using unauthenticated requests (lower rate limits).[/warning]")

    # Call the renamed function
    user_repositories, total_stars, top_10_repo_names = get_user_repositories_stats(
        target_username,
        github_token,
        console
    )

    if user_repositories is not None: # Check if the fetch was successful
        console.print(f"[info]Successfully retrieved data for {len(user_repositories)} repositories.[/]")

        # --- Display Table (Rich) ---
        table = Table(
            title=f"GitHub Repository Statistics for {target_username}",
            show_header=True,
            header_style="header",
            expand=False # Prevent table from expanding excessively
        )
        table.add_column("Repository", style="repo_name", min_width=20, max_width=30, overflow="ellipsis")
        table.add_column("Description", style="description", max_width=45, overflow="ellipsis") # Limit width
        table.add_column("⭐", style="stars", justify="right") # Use Icon
        table.add_column("🍴", style="forks", justify="right") # Use Icon
        table.add_column("C", style="commits", justify="right") # Abbreviate Header
        table.add_column("U", style="contributors", justify="right") # Abbreviate Header
        table.add_column("# Issues", style="issues", justify="right") # Header clarifies 'Closed Issues'
        table.add_column("Updated", style="last_update", justify="right") # Abbreviate Header
        table.add_column("Avg Issue Res.", style="avg_resolution", justify="right", min_width=12) # Abbreviate Header

        for repo in user_repositories:
            # Format numbers with commas for table too
            stars_str = f"{repo.get('stars', 0):,}"
            forks_str = f"{repo.get('forks', 0):,}"
            commits_str = f"{repo.get('commit_count', 0):,}" if repo.get('commit_count') is not None else "N/A"
            contrib_str = f"{repo.get('contributors_count', 0):,}" if repo.get('contributors_count') is not None else "N/A"
            issues_str = f"{repo.get('closed_issues_count', 0):,}" if repo.get('closed_issues_count') is not None else "N/A"

            resolution_time_str = format_resolution_time(repo.get('avg_issue_resolution_time'))
            # Create a Text object for the link
            repo_link = Text.from_markup(f"[{repo.get('name', 'N/A')}]({repo.get('url', '#')})")

            table.add_row(
                repo_link,
                repo.get('description', ''), # Use get with default
                stars_str,
                forks_str,
                commits_str,
                contrib_str,
                issues_str,
                repo.get('last_update_str', 'Unknown'), # Use get with default
                resolution_time_str,
            )
        console.print(table)

        console.print(f"\n[total_stars]Total Stars Across All Repositories: {total_stars:,}[/]")

        # --- Save to JSON ---
        json_data = {
            'username': target_username,
            'fetch_time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'total_stars': total_stars,
            'repositories': user_repositories, # Contains all collected data
        }
        save_to_json(json_data, filename=f"{target_username}_github_stats.json")

        # --- Create Markdown Table ---
        # Pass the correct list of full names for the chart
        create_markdown_table(user_repositories, total_stars, top_10_repo_names, target_username, filename=f"{target_username}_github_stats.md")

    else:
        # Handle case where get_user_repositories_stats returned None
        console.print(f"[error]Could not retrieve repository data for {target_username}. Please check logs or username.[/error]")

    end_time = time.time()
    console.print(f"[info]Script finished in {end_time - start_time:.2f} seconds.[/info]")
