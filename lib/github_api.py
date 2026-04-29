"""HTTP client for the GitHub REST API with retries, backoff, and rate-limit awareness."""

import logging
import time
from urllib.parse import parse_qs, urlparse

import requests

GITHUB_API_BASE_URL = "https://api.github.com"
REQUEST_TIMEOUT = 15
DEFAULT_PAGE_SIZE = 100
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 1
MAX_RETRY_DELAY = 60


def make_github_request(url, headers, params=None, console=None, retries=MAX_RETRIES):
    """Make a request to the GitHub API with error handling, rate-limit awareness, and retries."""
    current_retry = 0
    delay = INITIAL_RETRY_DELAY
    while current_retry <= retries:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)

            remaining_requests = response.headers.get('X-RateLimit-Remaining')
            if remaining_requests is not None:
                try:
                    if int(remaining_requests) < 10:
                        logging.warning(f"Low rate limit remaining ({remaining_requests}). Adding small delay.")
                        time.sleep(0.5)
                except ValueError:
                    pass

            if response.status_code == 403 and "Retry-After" in response.headers:
                try:
                    retry_after = int(response.headers["Retry-After"])
                    wait_time = max(retry_after, delay)
                    wait_time = min(wait_time, 300)
                    logging.warning(f"Rate limit hit for {url}. Retrying after {wait_time} seconds.")
                    if console:
                        console.print(f"[yellow]Rate limit hit. Waiting {wait_time}s...[/yellow]", end=" ")
                    time.sleep(wait_time)
                    if console:
                        console.print("[yellow]Resuming.[/yellow]")
                    delay = INITIAL_RETRY_DELAY
                    continue
                except ValueError:
                    logging.warning(f"Rate limit hit for {url}, but couldn't parse Retry-After header: {response.headers['Retry-After']}. Falling back to exponential backoff.")

            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            logging.warning(f"Request timed out for {url} (Attempt {current_retry+1}/{retries+1}): {e}")
        except requests.exceptions.RequestException as e:
            status_code = getattr(getattr(e, 'response', None), 'status_code', None)
            logging.error(f"Request failed for {url} (Attempt {current_retry+1}/{retries+1}, Status: {status_code}): {e}")

            if status_code == 404:
                logging.warning(f"Resource not found (404) at {url}. Aborting retries for this request.")
                return None
            if status_code == 401:
                logging.error(f"Authorization failed (401) for {url}. Check your GitHub token. Aborting retries.")
                if console:
                    console.print(f"[bold red]Authorization Error (401) for {url}. Check token.[/bold red]")
                return None
            if status_code == 403:
                logging.error(f"Forbidden (403) accessing {url}. Check permissions or scope. Aborting retries.")
                if console:
                    console.print(f"[bold red]Access Forbidden (403) for {url}. Check permissions/scope.[/bold red]")
                return None

        current_retry += 1
        if current_retry <= retries:
            actual_delay = min(delay, MAX_RETRY_DELAY)
            logging.info(f"Retrying {url} in {actual_delay} seconds...")
            if console:
                error_type = type(e).__name__ if 'e' in locals() else 'Unknown Error'
                console.print(f"[yellow]Request failed ({error_type}). Retrying in {actual_delay}s...[/yellow]", end=" ")
            time.sleep(actual_delay)
            if console:
                console.print("[yellow]Retrying.[/yellow]")
            delay *= 2
        else:
            logging.error(f"Max retries reached for {url}.")
            if console:
                console.print(f"[red]Failed to fetch {url} after {retries} retries.[/red]")
            return None

    return None


def get_count_from_link_header(response):
    """Estimate total item count from the Link header's 'last' relation (per_page=1 only)."""
    if not response or 'Link' not in response.headers:
        return None
    link_header = response.headers['Link']
    links = link_header.split(',')
    last_page_num = None
    request_per_page = None

    if response.request and response.request.url:
        try:
            query_params = urlparse(response.request.url).query
            parsed_params = parse_qs(query_params)
            if 'per_page' in parsed_params:
                request_per_page = int(parsed_params['per_page'][0])
        except (ValueError, KeyError, IndexError, TypeError):
            logging.warning(f"Could not parse per_page from request URL: {response.request.url}", exc_info=True)

    for link in links:
        parts = link.split(';')
        if len(parts) == 2:
            url_part = parts[0].strip('<> ')
            rel_part = parts[1].strip()

            if rel_part == 'rel="last"':
                try:
                    query_params = urlparse(url_part).query
                    parsed_params = parse_qs(query_params)
                    if 'page' in parsed_params:
                        last_page_num = int(parsed_params['page'][0])
                    elif 'page=' in url_part:
                        last_page_num = int(url_part.split('page=')[-1].split('&')[0])
                    break
                except (ValueError, IndexError, KeyError, TypeError) as e:
                    logging.warning(f"Could not parse page number from 'last' link: {link}. Error: {e}", exc_info=True)
                    return None

    if last_page_num is not None:
        if request_per_page == 1:
            return last_page_num
        else:
            logging.warning(f"Link header found, but request used per_page={request_per_page} (expected 1 for count estimation). Cannot reliably estimate total count via Link header.")
            return None

    return None
