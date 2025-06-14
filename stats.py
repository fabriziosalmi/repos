# -*- coding: utf-8 -*-
import os
import requests
import datetime
import time
import json
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.theme import Theme
from rich.text import Text
import logging
from urllib.parse import urlparse, parse_qs # IMPORT parse_qs HERE
from urllib.parse import quote as url_quote
# Import the HTML generation module
import stats2html

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

# Cache configuration
CACHE_FILE = "github_stats_cache.json"
CACHE_DURATION_HOURS = 1  # Cache valid for 1 hour

# --- Helper Functions ---

def load_cache():
    """Load cached data if it exists and is still valid."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            cache_time = datetime.datetime.fromisoformat(cache_data.get('timestamp', ''))
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # Check if cache is still valid
            if (now - cache_time).total_seconds() < CACHE_DURATION_HOURS * 3600:
                logging.info("Using cached data (still valid)")
                return cache_data.get('data')
                
        logging.info("Cache not found or expired")
        return None
    except Exception as e:
        logging.warning(f"Error loading cache: {e}")
        return None

def save_cache(data):
    """Save data to cache."""
    try:
        cache_data = {
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'data': data
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, default=str)
        logging.info("Data cached successfully")
    except Exception as e:
        logging.warning(f"Error saving cache: {e}")

def validate_data_completeness(repositories, total_stars):
    """Validate that the collected data is complete and not corrupted."""
    if not repositories or not isinstance(repositories, list):
        return False, "No repositories found or invalid data format"
    
    if total_stars < 0:
        return False, "Invalid total stars count"
    
    # Check for essential fields in repositories
    required_fields = ['name', 'full_name', 'description', 'stars', 'url']
    for repo in repositories:
        if not isinstance(repo, dict):
            return False, f"Invalid repository data format: {type(repo)}"
        
        for field in required_fields:
            if field not in repo:
                return False, f"Missing required field '{field}' in repository data"
    
    logging.info(f"Data validation passed: {len(repositories)} repositories, {total_stars} total stars")
    return True, "Data validation successful"

def safe_file_write(filename, write_func):
    """Safely write to a file with backup and validation."""
    backup_file = f"{filename}.backup"
    temp_file = f"{filename}.tmp"
    
    try:
        # Create backup if original exists
        if os.path.exists(filename):
            import shutil
            shutil.copy2(filename, backup_file)
            logging.info(f"Created backup: {backup_file}")
        
        # Write using the provided function - handle different function signatures
        try:
            # Most write functions expect a filename parameter
            write_func()
            
            # Check if the target file was created
            if os.path.exists(filename):
                # File was created successfully
                pass
            else:
                raise IOError(f"Write function did not create the expected file: {filename}")
                
        except Exception as write_error:
            logging.error(f"Error during write operation: {write_error}")
            raise
        
        # Verify file exists and has content
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            raise IOError("Output file is empty or doesn't exist")
        
        logging.info(f"Successfully wrote {filename}")
        
        # Clean up backup after successful write
        if os.path.exists(backup_file):
            os.remove(backup_file)
        
        return True
            
    except Exception as e:
        logging.error(f"Error writing {filename}: {e}")
        
        # Restore from backup if it exists
        if os.path.exists(backup_file):
            try:
                import shutil
                if os.path.exists(filename):
                    os.remove(filename)
                shutil.move(backup_file, filename)
                logging.info(f"Restored {filename} from backup")
            except Exception as restore_error:
                logging.error(f"Failed to restore backup: {restore_error}")
        
        # Clean up temp file
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        
        return False

def get_human_readable_time(timestamp):
    """Converts a timezone-aware datetime object to a human-readable time difference."""
    # Ensure timestamp is timezone-aware (expecting UTC from GitHub API)
    if not isinstance(timestamp, datetime.datetime):
        # If it's not a datetime object, we can't process it
        logging.warning(f"Invalid timestamp type received: {type(timestamp)}. Returning 'Unknown'.")
        return "Unknown"
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
            # Use remaining requests header for proactive delay? (X-RateLimit-Remaining)
            remaining_requests = response.headers.get('X-RateLimit-Remaining')
            if remaining_requests is not None:
                try:
                    if int(remaining_requests) < 10: # Be cautious when requests are low
                        logging.warning(f"Low rate limit remaining ({remaining_requests}). Adding small delay.")
                        time.sleep(0.5)
                except ValueError:
                    pass # Ignore if header is not an integer

            if response.status_code == 403 and "Retry-After" in response.headers:
                try:
                    retry_after = int(response.headers["Retry-After"])
                    wait_time = max(retry_after, delay) # Wait at least the requested time
                    wait_time = min(wait_time, 300) # Cap max wait time for Retry-After to 5 mins
                    logging.warning(f"Rate limit hit for {url}. Retrying after {wait_time} seconds.")
                    if console:
                        console.print(f"[yellow]Rate limit hit. Waiting {wait_time}s...[/yellow]", end=" ")
                    time.sleep(wait_time)
                    if console:
                        console.print("[yellow]Resuming.[/yellow]")
                    # Don't increment retry count for explicit rate limit waits requested by GitHub
                    delay = INITIAL_RETRY_DELAY # Reset delay after successful wait
                    continue # Retry the request
                except ValueError:
                     logging.warning(f"Rate limit hit for {url}, but couldn't parse Retry-After header: {response.headers['Retry-After']}. Falling back to exponential backoff.")
                     # Fall through to exponential backoff if header is invalid

            response.raise_for_status() # Raise HTTPError for other bad responses (4xx or 5xx)
            return response # Success

        except requests.exceptions.Timeout as e:
            logging.warning(f"Request timed out for {url} (Attempt {current_retry+1}/{retries+1}): {e}")
        except requests.exceptions.RequestException as e:
            status_code = getattr(getattr(e, 'response', None), 'status_code', None)
            logging.error(f"Request failed for {url} (Attempt {current_retry+1}/{retries+1}, Status: {status_code}): {e}")

            if status_code == 404:
                 logging.warning(f"Resource not found (404) at {url}. Aborting retries for this request.")
                 return None # Return None for 404
            if status_code == 401:
                 logging.error(f"Authorization failed (401) for {url}. Check your GitHub token. Aborting retries.")
                 if console:
                     console.print(f"[bold red]Authorization Error (401) for {url}. Check token.[/bold red]")
                 return None # Return None for 401
            if status_code == 403:
                 # Handle general 403 Forbidden (not rate limit related, e.g., permissions)
                 logging.error(f"Forbidden (403) accessing {url}. Check permissions or scope. Aborting retries.")
                 if console:
                     console.print(f"[bold red]Access Forbidden (403) for {url}. Check permissions/scope.[/bold red]")
                 return None # Return None for permission issues

        # If caught an exception or non-handled error, prepare for retry
        current_retry += 1
        if current_retry <= retries:
            actual_delay = min(delay, MAX_RETRY_DELAY) # Ensure delay respects max cap
            logging.info(f"Retrying {url} in {actual_delay} seconds...")
            if console:
                 # Provide more context on the error type if possible
                 error_type = type(e).__name__ if 'e' in locals() else 'Unknown Error'
                 console.print(f"[yellow]Request failed ({error_type}). Retrying in {actual_delay}s...[/yellow]", end=" ")
            time.sleep(actual_delay)
            if console:
                 console.print("[yellow]Retrying.[/yellow]")
            delay *= 2 # Exponential backoff
        else:
            logging.error(f"Max retries reached for {url}.")
            if console:
                console.print(f"[red]Failed to fetch {url} after {retries} retries.[/red]")
            return None # Failed after all retries

    return None # Should not be reached, but included for safety

def get_count_from_link_header(response):
    """
    Estimates the total count of items based on the Link header's 'last' relation,
    assuming the request used per_page=1. Returns None otherwise or if header is missing/invalid.
    """
    if not response or 'Link' not in response.headers:
        return None
    link_header = response.headers['Link']
    links = link_header.split(',')
    last_page_num = None
    request_per_page = None # Try to determine per_page used in the request

    # Determine per_page from the request URL itself if possible
    if response.request and response.request.url:
        try:
            query_params = urlparse(response.request.url).query
            # FIX: Use parse_qs from urllib.parse
            parsed_params = parse_qs(query_params)
            if 'per_page' in parsed_params:
                 request_per_page = int(parsed_params['per_page'][0])
        except (ValueError, KeyError, IndexError, TypeError): # Added TypeError
            logging.warning(f"Could not parse per_page from request URL: {response.request.url}", exc_info=True)
            pass # Ignore if cannot parse

    for link in links:
        parts = link.split(';')
        if len(parts) == 2:
            url_part = parts[0].strip('<> ')
            rel_part = parts[1].strip()

            if rel_part == 'rel="last"':
                try:
                    query_params = urlparse(url_part).query
                    # FIX: Use parse_qs from urllib.parse
                    parsed_params = parse_qs(query_params)
                    if 'page' in parsed_params:
                        last_page_num = int(parsed_params['page'][0])
                    elif 'page=' in url_part: # Fallback parsing
                         last_page_num = int(url_part.split('page=')[-1].split('&')[0])
                    break # Found last link, no need to check others
                except (ValueError, IndexError, KeyError, TypeError) as e: # Added TypeError
                    logging.warning(f"Could not parse page number from 'last' link: {link}. Error: {e}", exc_info=True)
                    return None # Cannot determine count reliably

    if last_page_num is not None:
        # Only return count if we are confident request used per_page=1
        if request_per_page == 1:
             return last_page_num
        else:
            logging.warning(f"Link header found, but request used per_page={request_per_page} (expected 1 for count estimation). Cannot reliably estimate total count via Link header.")
            return None

    # If no 'last' link was found, it implies only one page of results.
    # The caller should handle this case by checking the response body length.
    return None

def get_average_issue_resolution_time(repo_full_name, headers, console):
    """Calculates the average time to resolve issues for a single repository."""
    issues_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/issues"
    total_resolution_seconds = 0.0 # Use float for accumulation
    closed_issue_count = 0
    page = 1
    processed_any_pages = False # Track if we successfully processed at least one page

    logging.info(f"Calculating avg issue resolution time for {repo_full_name}...")

    while True:
        params = {'state': 'closed', 'page': page, 'per_page': DEFAULT_PAGE_SIZE}
        response = make_github_request(issues_url, headers, params=params, console=console)

        if response is None:
            logging.warning(f"Could not retrieve closed issues page {page} for {repo_full_name}. Stopping calculation.")
            # Return None if we failed to get *any* data, or partial data if we got some
            if not processed_any_pages:
                return None # Indicate complete failure
            else:
                # Return average based on pages processed so far
                return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else 0.0

        processed_any_pages = True # Mark that we got at least one page response
        try:
            issues = response.json()
            if not isinstance(issues, list):
                 logging.error(f"Unexpected JSON response type for issues of {repo_full_name} (page {page}): {type(issues)}")
                 # Decide how to handle: stop or try next page? Stopping is safer.
                 return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else 0.0
        except json.JSONDecodeError:
             logging.error(f"Failed to decode JSON response for closed issues of {repo_full_name}, page {page}.")
             # Return average based on pages processed so far
             return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else 0.0


        if not issues:
            logging.debug(f"No more issues found on page {page} for {repo_full_name}.")
            break # No more issues on this page or subsequent pages

        valid_issues_on_page = 0
        for issue in issues:
            # Ensure it's an issue and not a pull request, and has necessary dates
            if isinstance(issue, dict) and 'pull_request' not in issue and issue.get('created_at') and issue.get('closed_at'):
                created_at = parse_github_datetime(issue['created_at'])
                closed_at = parse_github_datetime(issue['closed_at'])

                if created_at and closed_at:
                    # Ensure closed_at is not before created_at (allow same time)
                    if closed_at >= created_at:
                        resolution_time = (closed_at - created_at).total_seconds()
                        total_resolution_seconds += resolution_time
                        closed_issue_count += 1
                        valid_issues_on_page += 1
                    else:
                        # Log as info, might happen with API quirks or bulk closing
                        logging.info(f"Issue #{issue.get('number')} in {repo_full_name} closed at {closed_at} before creation at {created_at}. Skipping.")
                #else: # No need to log here, parse_github_datetime already warns
                #     logging.warning(f"Could not parse dates for issue {issue.get('number')} in {repo_full_name}. Skipping.")
            elif not isinstance(issue, dict):
                logging.warning(f"Unexpected item type in issues list for {repo_full_name}: {type(issue)}")

        logging.debug(f"Processed page {page} for {repo_full_name}, found {len(issues)} items, {valid_issues_on_page} valid closed issues.")

        # Check if there's a next page using Link header (more reliable than just checking list emptiness)
        if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
             page += 1
             # Optional: Add a small delay between pages to be polite to the API
             time.sleep(0.1)
        else:
             logging.debug(f"No 'next' link found on page {page} for {repo_full_name}. Assuming last page.")
             break # No 'next' link found, assume this was the last page

    if closed_issue_count > 0:
        average_seconds = total_resolution_seconds / closed_issue_count
        logging.info(f"Calculated average resolution time for {repo_full_name}: {average_seconds:.2f} seconds over {closed_issue_count} issues.")
        return average_seconds
    else:
        logging.info(f"No valid closed issues found for {repo_full_name} to calculate average resolution time.")
        # Return 0.0 if processed pages but found no valid issues
        # Return None if failed to process any pages (handled earlier)
        return 0.0

def get_repository_languages(repo_full_name, headers, console):
    """Fetch repository languages and their usage statistics."""
    languages_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/languages"
    response = make_github_request(languages_url, headers, console=console)
    
    if response is None:
        return {}
    
    try:
        languages = response.json()
        if not isinstance(languages, dict):
            logging.warning(f"Unexpected response format for languages of {repo_full_name}")
            return {}
        
        # Calculate percentages
        total_bytes = sum(languages.values())
        if total_bytes == 0:
            return {}
        
        language_stats = {}
        for language, bytes_count in languages.items():
            percentage = (bytes_count / total_bytes) * 100
            language_stats[language] = {
                'bytes': bytes_count,
                'percentage': round(percentage, 2)
            }
        
        # Sort by percentage descending
        sorted_languages = dict(sorted(language_stats.items(), 
                                     key=lambda x: x[1]['percentage'], 
                                     reverse=True))
        
        return sorted_languages
        
    except json.JSONDecodeError:
        logging.warning(f"Failed to decode languages JSON for {repo_full_name}")
        return {}
    except Exception as e:
        logging.warning(f"Error fetching languages for {repo_full_name}: {e}")
        return {}

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
            # Sort by full_name for potentially more consistent pagination if names change rarely.
            params = {'page': page, 'per_page': DEFAULT_PAGE_SIZE, 'type': 'owner', 'sort': 'full_name'}
            response = make_github_request(url, headers, params=params, console=console)

            if response is None:
                console.print(f"[red]Failed to fetch repository list (page {page}) for {username} after multiple retries. Aborting.[/red]")
                return None, None, [] # Return indicating failure

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
                break # No more repositories

            logging.info(f"Processing page {page} of repositories ({len(repos)} found).")
            # Use a temporary list for tracking on this page
            page_repo_names = []
            for repo in track(repos, description=f"Processing basic repo info (page {page})...", console=console, transient=True):
                # Basic validation of repo item structure
                if not isinstance(repo, dict):
                     logging.warning(f"Skipping invalid item in repository list: {type(repo)}")
                     continue

                full_name = repo.get('full_name')
                if not full_name:
                    logging.warning(f"Skipping repository with missing 'full_name': {repo.get('name')}")
                    continue

                # Skip archived/disabled repos? Add option later.
                # if repo.get('archived'): continue
                # if repo.get('disabled'): continue

                # Store initial data, initialize detailed fields
                repo_data[full_name] = {
                    'url': repo.get('html_url', '#'), # Use '#' as fallback URL
                    'name': repo.get('name', 'N/A'),
                    'full_name': full_name, # Store full_name for later API calls
                    'description': repo.get('description') or "No description", # Ensure description is never None
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'watchers': repo.get('watchers_count', 0),  # Add watchers count
                    'language': repo.get('language', 'Not specified'),  # Primary language
                    'archived': repo.get('archived', False),  # Archived status
                    'disabled': repo.get('disabled', False),  # Disabled status
                    'private': repo.get('private', False),  # Private status
                    'fork': repo.get('fork', False),  # Fork status
                    'license': repo.get('license', {}).get('name') if repo.get('license') else 'No license',  # License
                    'default_branch': repo.get('default_branch', 'main'),  # Default branch
                    'open_issues_count': repo.get('open_issues_count', 0),  # Open issues count
                    'size': repo.get('size', 0),  # Repository size in KB
                    # Use pushed_at for a better sense of recent code activity, fallback to updated_at
                    'last_update_api': parse_github_datetime(repo.get('pushed_at') or repo.get('updated_at')),
                    'created_at_api': parse_github_datetime(repo.get('created_at')),
                    'has_issues': repo.get('has_issues', False), # Store this info from list endpoint
                    # Initialize fields to be fetched later
                    'commit_count': None, # Use None to indicate not yet fetched or failed
                    'contributors_count': None,
                    'last_update_str': "Fetching...",
                    'avg_issue_resolution_time': None, # None indicates not calculated or error
                    'closed_issues_count': None, # Using closed_issues_count for clarity
                    'processed_details': False # Flag to indicate if detailed info fetch was attempted
                }
                page_repo_names.append(full_name)
                total_stars += repo_data[full_name]['stars']

            all_repo_names.extend(page_repo_names)

            # Check for next page via Link header
            if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
                 page += 1
                 time.sleep(0.2) # Small delay between page requests
            else:
                 break # No 'next' link, assume last page


        logging.info(f"Fetched basic info for {len(all_repo_names)} repositories. Total stars: {total_stars:,}.")
        logging.info("Fetching detailed information for each repository...")

        # --- Process each repository to get detailed info ---
        repo_keys_to_process = list(repo_data.keys())
        for full_name in track(repo_keys_to_process, description="Fetching detailed info", console=console):
            if full_name not in repo_data: # Safety check
                logging.warning(f"Full name '{full_name}' from key list not found in repo_data dict. Skipping.")
                continue
            repo_info = repo_data[full_name]
            repo_api_url_base = f"{GITHUB_API_BASE_URL}/repos/{full_name}"

            # Skip if already processed (useful if script supports resuming)
            if repo_info['processed_details']:
                continue

            try:
                # --- Commit Count ---
                # Using the Link header estimation method with per_page=1
                commits_url = f"{repo_api_url_base}/commits"
                commits_response_count = make_github_request(commits_url, headers, params={'per_page': 1}, console=console)
                commit_count = None # Default to None (unknown/error)

                if commits_response_count:
                     link_count = get_count_from_link_header(commits_response_count) # Expects per_page=1
                     if link_count is not None:
                         commit_count = link_count
                     elif commits_response_count.status_code == 200: # If no Link header, check response body
                         try:
                             commits_json = commits_response_count.json()
                             # If per_page=1, len is 0 (empty repo) or 1 (at least one commit).
                             # This correctly represents the count when there's no "last" link.
                             commit_count = len(commits_json) if isinstance(commits_json, list) else 0
                         except (json.JSONDecodeError, TypeError):
                             logging.warning(f"Could not decode commits JSON for {full_name} when Link header was missing.")
                             commit_count = 0 # Fallback
                     # Handle 409 Conflict for Empty Git Repository
                     elif commits_response_count.status_code == 409:
                          logging.info(f"Repository {full_name} is empty (409 conflict on commits). Setting commit count to 0.")
                          commit_count = 0
                     else:
                         logging.warning(f"Could not determine commit count for {full_name} via Link header. Status: {commits_response_count.status_code}")
                         commit_count = 0 # Fallback
                else:
                    logging.warning(f"Failed request for commit count link header for {full_name}.")
                    # commit_count remains None

                repo_info['commit_count'] = commit_count


                # --- Contributors Count ---
                contributors_url = f"{repo_api_url_base}/contributors"
                # Use per_page=1 trick with Link header again
                contrib_response = make_github_request(contributors_url, headers, params={'per_page': 1, 'anon': 'true'}, console=console)
                contributors_count = None # Default to None

                if contrib_response:
                    link_count = get_count_from_link_header(contrib_response) # Expects per_page=1
                    if link_count is not None:
                        contributors_count = link_count
                    elif contrib_response.status_code == 200:
                         try:
                            contributors_json = contrib_response.json()
                            contributors_count = len(contributors_json) if isinstance(contributors_json, list) else 0
                         except (json.JSONDecodeError, TypeError):
                            logging.warning(f"Could not decode contributors JSON for {full_name} when Link header was missing.")
                            contributors_count = 0
                    # Handle 204 No Content: contributors list might be generated async by GitHub
                    elif contrib_response.status_code == 204:
                         logging.info(f"Repo {full_name} reported 204 No Content for contributors (may still be processing). Setting count to 0 for now.")
                         contributors_count = 0
                    else:
                         logging.warning(f"Could not determine contributor count for {full_name}. Status: {contrib_response.status_code}")
                         contributors_count = 0 # Fallback
                else:
                    logging.warning(f"Failed request for contributor count for {full_name}.")
                    # contributors_count remains None

                repo_info['contributors_count'] = contributors_count

                # --- Last Update String ---
                if repo_info['last_update_api']:
                    repo_info['last_update_str'] = get_human_readable_time(repo_info['last_update_api'])
                else:
                    repo_info['last_update_str'] = "Unknown"


                # --- Average Issue Resolution Time ---
                # Use 'has_issues' flag fetched earlier
                has_issues = repo_info.get('has_issues', True) # Default to True if somehow missing
                avg_res_time_secs = None # Default to None (error/not applicable)

                if has_issues:
                     avg_res_time_secs = get_average_issue_resolution_time(full_name, headers, console)
                     # get_average_issue_resolution_time returns 0.0 for no closed issues, None for error
                else:
                     logging.info(f"Skipping issue resolution calculation for {full_name} as issues are disabled.")
                     avg_res_time_secs = 0.0 # Represent 'issues disabled' as 0.0 average time

                repo_info['avg_issue_resolution_time'] = avg_res_time_secs

                # --- Get the number of closed issues ---
                closed_issues_count = None # Default to None

                if has_issues:
                    # Only try to get count if issues are enabled. Avg calc failure (None) is separate.
                    issues_url = f"{repo_api_url_base}/issues"
                    # Use per_page=1 trick with Link header
                    issues_response = make_github_request(issues_url, headers, params={'state': 'closed', 'per_page': 1}, console=console)
                    if issues_response:
                        link_count = get_count_from_link_header(issues_response) # Expects per_page=1
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
                             closed_issues_count = 0 # Fallback
                    else:
                         logging.warning(f"Failed request for closed issue count for {full_name}.")
                         # closed_issues_count remains None
                else: # Issues disabled
                     closed_issues_count = 0 # Issues disabled means 0 closed issues

                repo_info['closed_issues_count'] = closed_issues_count

                # --- Language Statistics ---
                # Only fetch language stats for active repositories to optimize API usage
                if not repo_info.get('archived', False) and not repo_info.get('disabled', False):
                    language_stats = get_repository_languages(full_name, headers, console)
                    repo_info['language_stats'] = language_stats
                    
                    # Update primary language if we have more detailed stats
                    if language_stats:
                        primary_language = list(language_stats.keys())[0]  # Most used language
                        repo_info['language'] = primary_language
                else:
                    repo_info['language_stats'] = {}

                repo_info['processed_details'] = True
                # Optional delay between detailed fetches for different repos
                time.sleep(0.1) # Slightly longer delay to be respectful to API

            except Exception as e:
                # Catch broader errors during processing of a single repo
                logging.error(f"Unexpected error processing details for {full_name}: {e}", exc_info=True)
                console.print(f"  [red]Error processing details for {full_name}: {e}. Skipping details.[/red]")
                # Mark as processed (attempted) but leave detailed fields as None/defaults
                repo_info['processed_details'] = True # Mark attempt even if failed
                continue # Process the next repo

    except Exception as e:
        # Catch unexpected errors during the overall process (e.g., initial setup)
        logging.error(f"An unexpected error occurred during repository fetching/processing: {e}", exc_info=True)
        console.print(f"[bold red]An critical error occurred: {e}[/]")
        return None, None, []

    # --- Sort the repositories after all info is gathered ---
    # Convert repo_data dict values to a list
    processed_repos = list(repo_data.values())
    # Sort by stars descending, handle potential None values gracefully (treat as 0)
    processed_repos.sort(key=lambda repo: repo.get('stars', 0) or 0, reverse=True)

    # Get top 10 repo *full_names* for the chart URL (ensure they exist)
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
                # Add handling for other non-serializable types if needed
                # For example, if you store sets:
                # if isinstance(o, set):
                #     return list(o)
                try:
                    # Attempt standard JSON serialization first
                    json.dumps(o)
                    return o
                except TypeError:
                    # Fallback to string representation if not serializable
                    return str(o)

            json.dump(data, f, indent=4, default=dt_converter, ensure_ascii=False)
        logging.info(f"Data successfully saved to {filename}")
        print(f"Data saved to {filename}") # User feedback
    except (IOError, TypeError) as e:
        logging.error(f"Error saving data to JSON file '{filename}': {e}")
        print(f"Error saving to JSON: {e}") # User feedback

def format_resolution_time(seconds):
    """Formats resolution time in seconds into a human-readable string (d, h, m, s)."""
    if seconds is None:
        return "N/A" # Error during calculation or not applicable
    if not isinstance(seconds, (int, float)):
        logging.warning(f"Invalid type ({type(seconds)}) passed to format_resolution_time.")
        return "Error"

    if seconds < 0:
        logging.warning(f"Negative resolution time ({seconds}s) passed to formatter.")
        return "Invalid Data" # Should not happen

    # Handle the case where 0 means "No Closed Issues" or "Issues Disabled" based on context
    if abs(seconds) < 0.001: # Use tolerance for float comparison
        return "No Closed Issues" # Simplification for display

    # Ensure seconds is treated as float for precision before divmod
    seconds = float(seconds)

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, sec = divmod(remainder, 60)

    parts = []
    if days >= 1:
        parts.append(f"{int(days)}d")
    # Only show hours/minutes/seconds if days < threshold? Or always show? Always show for now.
    if hours >= 1:
        parts.append(f"{int(hours)}h")
    if minutes >= 1:
        parts.append(f"{int(minutes)}m")
    # Show seconds if > 0.1s or if it's the only unit and total time < 1 minute
    if sec > 0.1 or (not parts and seconds > 0):
        # Use fewer decimals for larger timespans?
        if days > 0 or hours > 0:
             parts.append(f"{int(sec)}s") # Integer seconds if days/hours present
        elif seconds < 3600: # Show decimal seconds only if total time < 1 hour
             parts.append(f"{sec:.1f}s")
        else:
             parts.append(f"{int(sec)}s")

    return " ".join(parts) if parts else "~0s" # If calculation resulted in value < 0.1s

def create_markdown_table(repositories, total_stars, top_repo_full_names, username, filename="github_stats.md"):
    """Creates a Markdown file with summary, chart, and detailed table."""
    logging.info(f"Generating Markdown report '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# GitHub Repository Stats for {username}\n\n")
            f.write(f"Total stars across owned repositories scanned: **{total_stars:,}** ⭐\n\n") # Use markdown bold and formatting

            # GitHub Readme Stats Card (Dynamic Username)
            f.write(f"## Overall Stats\n\n")
            # Added cache_seconds=3600 (1 hour) to reduce load on vercel app
            # Use a theme consistent with potential dark mode READMEs
            stats_card_url = f"https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=github_dark&hide_border=true&cache_seconds=3600"
            streak = f"https://streak-stats.demolab.com/?user={username}"
            trophy = f"https://github-profile-trophy.vercel.app/?username={username}"
            f.write(f"![{username}'s GitHub stats]({stats_card_url})\n\n")
            f.write(f"![{username}'s GitHub streak]({streak})\n\n")
            f.write(f"![{username}'s GitHub trophy]({trophy})\n\n")

            # Star History Chart (Top N Repos)
            if top_repo_full_names:
                # Limit number of repos in chart URL to avoid excessive length (e.g., max 10)
                num_chart_repos = min(len(top_repo_full_names), 10)
                chart_repo_names = top_repo_full_names[:num_chart_repos]
                f.write(f"## Star History (Top {num_chart_repos} Repositories by Stars)\n\n")
                # URL encode repository names
                repo_list_param = ",".join(url_quote(name) for name in chart_repo_names)
                # Use HTTPS for the chart URL
                chart_url = f"https://api.star-history.com/svg?repos={repo_list_param}&type=Date&theme=dark"
                f.write(f"[![Star History Chart]({chart_url})](https://star-history.com/#{"&".join(repo_list_param.split(','))}&Date)\n\n") # Link chart to interactive version
            else:
                 f.write("*(Could not generate star history chart - no repositories found or an error occurred)*\n\n")

            # Detailed Repository Table
            f.write(f"## Repository Details\n\n")
            # Enhanced headers with new information
            f.write("| Repository | Description | Language 💻 | Stars ⭐ | Forks 🍴 | Watchers 👀 | Commits 💾 | Contributors 👥 | Issues ✅ | Last Update 🕒 | Status 📊 |\n")
            f.write("|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")

            for repo in repositories:
                # Sanitize description for Markdown table cells
                description = repo.get('description', 'No description')
                description = description.replace("|", "\\|") # Escape pipe characters
                description = description.replace("\n", "<br>") # Keep newlines visually
                
                # Truncate long descriptions
                if len(description) > 50:
                    description = description[:47] + "..."

                # Get language info
                language = repo.get('language', 'N/A')
                if language == 'Not specified':
                    language = 'N/A'

                # Get status indicator (convert rich markup to simple text for markdown)
                status_indicator = get_repository_status_indicator(repo)
                # Remove rich markup for markdown
                status_text = status_indicator
                if '[' in status_text and ']' in status_text:
                    # Extract just the emoji and text part
                    import re
                    match = re.search(r'[^[]*\]([^[]*)\[', status_text)
                    if match:
                        status_text = match.group(1)
                    else:
                        # Fallback: just remove the markup
                        status_text = re.sub(r'\[[^\]]*\]', '', status_text)

                # Format numbers, handle N/A
                stars_str = f"{repo.get('stars', 0):,}"
                forks_str = f"{repo.get('forks', 0):,}"
                watchers_str = f"{repo.get('watchers', 0):,}"

                commits_val = repo.get('commit_count')
                commits_str = f"{commits_val:,}" if commits_val is not None else "N/A"

                contrib_val = repo.get('contributors_count')
                contrib_str = f"{contrib_val:,}" if contrib_val is not None else "N/A"

                issues_val = repo.get('closed_issues_count')
                issues_str = f"{issues_val:,}" if issues_val is not None else "N/A"

                last_update_str = repo.get('last_update_str', "Unknown")

                # Sanitize repo name for link text
                repo_name_sanitized = repo.get('name', 'N/A').replace('[', '\\[').replace(']', '\\]')
                repo_url = repo.get('url', '#')

                f.write(f"| [{repo_name_sanitized}]({repo_url}) "
                        f"| {description} "
                        f"| {language} "
                        f"| {stars_str} "
                        f"| {forks_str} "
                        f"| {watchers_str} "
                        f"| {commits_str} "
                        f"| {contrib_str} "
                        f"| {issues_str} "
                        f"| {last_update_str} "
                        f"| {status_text} |\n")

        logging.info(f"Markdown report saved to {filename}")
        print(f"Markdown report saved to {filename}") # User feedback

    except IOError as e:
        logging.error(f"Error writing Markdown file '{filename}': {e}")
        print(f"Error creating Markdown file: {e}") # User feedback
    except Exception as e:
        # Catch potential errors during string formatting or file writing
        logging.error(f"An unexpected error occurred during Markdown generation: {e}", exc_info=True)
        print(f"An unexpected error occurred creating Markdown file: {e}")

# --- Main Execution Block ---

if __name__ == '__main__':
    start_time = time.time()
def main():
    """Main function with comprehensive error handling and validation."""
    start_time = time.time()
    
    try:
        # For simplicity, keeping hardcoded username and env var token:
        target_username = 'fabriziosalmi'
        github_token = os.environ.get('MY_PAT')
        output_prefix = target_username

        # Configure Rich Console
        custom_theme = Theme({
            # FIX APPLIED: Removed 'link' from repo_name style
            "repo_name": "bold cyan",
            "description": "dim",
            "stars": "yellow",
            "forks": "blue",
            "commits": "magenta",
            "contributors": "green",
            "issues": "purple",
            "last_update": "default",
            "header": "bold white on blue",
            "total_stars": "bold yellow",
            "avg_resolution": "bold green",
            "info": "dim cyan",
            "warning": "yellow",
            "error": "bold red",
            "na": "dim" # Style for N/A values
        })
        console = Console(theme=custom_theme, record=False)

        console.print(f"[info]Fetching repository statistics for user: [bold]{target_username}[/bold]...[/]")
        if not github_token:
            console.print("[warning]Environment variable 'MY_PAT' not set. Using unauthenticated requests (lower rate limits).[/warning]")
        else:
            console.print("[info]Using GitHub token from MY_PAT environment variable.[/info]")

        # Check if we can use cached data
        cached_data = load_cache()
        if cached_data:
            console.print("[info]Using cached data to avoid API rate limits.[/info]")
            user_repositories = cached_data.get('repositories', [])
            total_stars = cached_data.get('total_stars', 0)
            top_10_repo_full_names = cached_data.get('top_10_repo_full_names', [])
        else:
            # Call the main data fetching function
            user_repositories, total_stars, top_10_repo_full_names = get_user_repositories_stats(
                target_username,
                github_token,
                console
            )
            
            # Save fetched data to cache
            if user_repositories is not None:
                cache_data = {
                    'repositories': user_repositories,
                    'total_stars': total_stars,
                    'top_10_repo_full_names': top_10_repo_full_names
                }
                save_cache(cache_data)

        if user_repositories is not None:
            # Validate data completeness before proceeding
            is_valid, validation_message = validate_data_completeness(user_repositories, total_stars)
            if not is_valid:
                console.print(f"[error]Data validation failed: {validation_message}[/error]")
                logging.error(f"Data validation failed: {validation_message}")
                return False

            repo_count = len(user_repositories)
            console.print(f"[info]Successfully retrieved data for {repo_count} repositories.[/]")

            # --- Display Table (Rich) ---
            if repo_count > 0:
                table = Table(
                    title=f"GitHub Repository Statistics for {target_username}",
                    show_header=True,
                    header_style="header",
                    expand=False,
                    show_lines=False,
                    padding=(0, 1)
                )
                
                # Add columns with enhanced information
                table.add_column("Repository", style="repo_name", min_width=18, max_width=25, overflow="ellipsis", justify="left", no_wrap=True)
                table.add_column("Description", style="description", max_width=35, overflow="ellipsis", justify="left", no_wrap=True)
                table.add_column("Language", style="info", min_width=8, max_width=12, overflow="ellipsis", justify="center", no_wrap=True)
                table.add_column("⭐", style="stars", justify="right", min_width=4)
                table.add_column("🍴", style="forks", justify="right", min_width=4)
                table.add_column("👀", style="info", justify="right", min_width=4, no_wrap=True)  # Watchers
                table.add_column("💾", style="commits", justify="right", min_width=5)
                table.add_column("👥", style="contributors", justify="right", min_width=4)
                table.add_column("✅", style="issues", justify="right", min_width=4)  # Closed issues
                table.add_column("Updated", style="last_update", justify="right", min_width=10, no_wrap=True)
                table.add_column("Status", style="info", justify="center", min_width=8, no_wrap=True)

                for repo in user_repositories:
                    # Handle repository status (archived, inactive, etc.)
                    status_indicator = get_repository_status_indicator(repo)
                    
                    # Format numbers with commas for table
                    stars_str = f"{repo.get('stars', 0):,}"
                    forks_str = f"{repo.get('forks', 0):,}"
                    watchers_str = f"{repo.get('watchers', 0):,}"

                    # Get primary language with fallback
                    language = repo.get('language', 'N/A')
                    if language == 'Not specified' or language == 'N/A':
                        language = "[dim]N/A[/]"
                    elif language:
                        # Truncate long language names
                        if len(language) > 10:
                            language = language[:8] + ".."

                    commits_val = repo.get('commit_count')
                    commits_str = f"{commits_val:,}" if commits_val is not None else "[na]N/A[/]"

                    contrib_val = repo.get('contributors_count')
                    contrib_str = f"{contrib_val:,}" if contrib_val is not None else "[na]N/A[/]"

                    issues_val = repo.get('closed_issues_count')
                    issues_str = f"{issues_val:,}" if issues_val is not None else "[na]N/A[/]"

                    # Simplified last update (remove "ago" to save space)
                    last_update_str = repo.get('last_update_str', '[na]Unknown[/]')
                    if last_update_str.endswith(' ago'):
                        last_update_str = last_update_str[:-4]  # Remove " ago"
                    # Simplified last update (remove "ago" to save space)
                    last_update_str = repo.get('last_update_str', '[na]Unknown[/]')
                    if last_update_str.endswith(' ago'):
                        last_update_str = last_update_str[:-4]  # Remove " ago"

                    # Create repository link
                    repo_name_display = repo.get('name', 'N/A')
                    repo_url = repo.get('url')
                    if repo_url and repo_url != '#':
                        repo_link_markup = f"[{repo_name_display}]({repo_url})"
                    else:
                        repo_link_markup = repo_name_display

                    # Ensure description is never None and truncate if too long
                    description = repo.get('description') or "No description provided"
                    if len(description) > 35:
                        description = description[:32] + "..."

                    table.add_row(
                        repo_link_markup,
                        description,
                        language,
                        stars_str,
                        forks_str,
                        watchers_str,
                        commits_str,
                        contrib_str,
                        issues_str,
                        last_update_str,
                        status_indicator,
                    )
                console.print(table)
            else:
                console.print(f"[info]No repositories found for user {target_username} to display in table.[/info]")

            console.print(f"\n[total_stars]Total Stars Across All Repositories: {total_stars:,}[/]")

            # --- Generate and Display Insights ---
            insights = generate_repository_insights(user_repositories)
            console.print(f"\n[header]📊 Repository Insights[/header]")
            
            # Language distribution
            if insights['top_languages']:
                console.print(f"[info]🔤 Top Languages:[/info]")
                for lang, count in insights['top_languages']:
                    percentage = (count / insights['total_repositories']) * 100
                    console.print(f"  • {lang}: {count} repos ({percentage:.1f}%)")
            
            # Activity insights
            console.print(f"\n[info]📈 Activity Status:[/info]")
            console.print(f"  • Active (≤30 days): {insights['activity_distribution']['active']} repos")
            console.print(f"  • Stale (30-180 days): {insights['activity_distribution']['stale']} repos")
            console.print(f"  • Inactive (>180 days): {insights['activity_distribution']['inactive']} repos")
            
            # Repository health
            console.print(f"\n[info]🏥 Repository Health:[/info]")
            console.print(f"  • Archived: {insights['archived_count']} repos")
            console.print(f"  • Forks: {insights['fork_count']} repos")
            console.print(f"  • Total Watchers: {insights['total_watchers']:,}")
            console.print(f"  • Open Issues: {insights['total_open_issues']:,}")

            # --- Save to JSON with safe file writing ---
            json_filename = f"{output_prefix}_github_stats.json"
            json_data = {
                'username': target_username,
                'fetch_time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'total_stars': total_stars,
                'repository_count': repo_count,
                'repositories': user_repositories,
            }
            
            def write_json():
                save_to_json(json_data, filename=json_filename)
            
            if not safe_file_write(json_filename, write_json):
                console.print(f"[error]Failed to write JSON file: {json_filename}[/error]")
                return False

            # --- Create Markdown Table with safe file writing ---
            md_filename = f"{output_prefix}_github_stats.md"
            
            def write_markdown():
                create_markdown_table(user_repositories, total_stars, top_10_repo_full_names, target_username, filename=md_filename)
            
            if not safe_file_write(md_filename, write_markdown):
                console.print(f"[error]Failed to write Markdown file: {md_filename}[/error]")
                return False

            # --- Create HTML Report with safe file writing ---
            html_filename = "docs/index.html"
            
            def write_html():
                stats2html.create_html_report(
                    user_repositories, 
                    total_stars, 
                    top_10_repo_full_names, 
                    target_username,
                    format_resolution_time
                )
            
            if not safe_file_write(html_filename, write_html):
                console.print(f"[error]Failed to write HTML file: {html_filename}[/error]")
                return False

            console.print("[info]All files generated successfully.[/info]")
            return True

        else:
            # Handle case where get_user_repositories_stats returned None
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


def get_repository_status_indicator(repo):
    """Generate status indicator for repository based on various criteria."""
    # Check archived status first (highest priority)
    if repo.get('archived', False):
        return "[yellow]📦 ARCHIVED[/yellow]"
    
    # Check disabled status
    if repo.get('disabled', False):
        return "[red]🚫 DISABLED[/red]"
    
    # Check if it's a fork
    if repo.get('fork', False):
        return "[cyan]🍴 FORK[/cyan]"
    
    # Check if repository is inactive (no updates in over 1 year)
    last_update = repo.get('last_update_api')
    if last_update:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            days_since_update = (now - last_update).days
            if days_since_update > 365:
                return "[dim]⚠️ INACTIVE[/dim]"
            elif days_since_update > 180:
                return "[dim]⏰ STALE[/dim]"
            elif days_since_update <= 7:
                return "[bright_green]🔥 ACTIVE[/bright_green]"
        except Exception:
            pass
    
    # Check if repository has no description
    if not repo.get('description') or repo.get('description') == "No description":
        return "[dim]📝 NO DESC[/dim]"
    
    # Check if it's a private repository
    if repo.get('private', False):
        return "[magenta]🔒 PRIVATE[/magenta]"
    
    # Active repository (default)
    return "[green]✅ ACTIVE[/green]"

def generate_repository_insights(repositories):
    """Generate insights about the repository collection."""
    if not repositories:
        return {}
    
    insights = {
        'total_repositories': len(repositories),
        'archived_count': 0,
        'fork_count': 0,
        'language_distribution': {},
        'size_distribution': {'small': 0, 'medium': 0, 'large': 0},
        'activity_distribution': {'active': 0, 'stale': 0, 'inactive': 0},
        'total_watchers': 0,
        'total_open_issues': 0,
        'top_languages': [],
        'repository_ages': {'new': 0, 'mature': 0, 'old': 0}
    }
    
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for repo in repositories:
        # Count archived and forks
        if repo.get('archived', False):
            insights['archived_count'] += 1
        if repo.get('fork', False):
            insights['fork_count'] += 1
            
        # Language distribution
        language = repo.get('language', 'Unknown')
        if language and language != 'Not specified':
            insights['language_distribution'][language] = insights['language_distribution'].get(language, 0) + 1
        
        # Size distribution (in KB)
        size = repo.get('size', 0)
        if size < 1000:  # < 1MB
            insights['size_distribution']['small'] += 1
        elif size < 10000:  # < 10MB
            insights['size_distribution']['medium'] += 1
        else:
            insights['size_distribution']['large'] += 1
        
        # Activity distribution
        last_update = repo.get('last_update_api')
        if last_update:
            days_since_update = (now - last_update).days
            if days_since_update <= 30:
                insights['activity_distribution']['active'] += 1
            elif days_since_update <= 180:
                insights['activity_distribution']['stale'] += 1
            else:
                insights['activity_distribution']['inactive'] += 1
        
        # Repository age
        created_at = repo.get('created_at_api')
        if created_at:
            days_old = (now - created_at).days
            if days_old <= 365:  # Less than 1 year
                insights['repository_ages']['new'] += 1
            elif days_old <= 1825:  # Less than 5 years
                insights['repository_ages']['mature'] += 1
            else:
                insights['repository_ages']['old'] += 1
        
        # Aggregate totals
        insights['total_watchers'] += repo.get('watchers', 0)
        insights['total_open_issues'] += repo.get('open_issues_count', 0)
    
    # Top languages (sorted by count)
    insights['top_languages'] = sorted(
        insights['language_distribution'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]  # Top 5 languages
    
    return insights
    
# --- Main Execution Block ---
if __name__ == '__main__':
    # Set up logging with more detailed configuration
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
    else:
        logging.info("Script execution completed successfully")
        sys.exit(0)



