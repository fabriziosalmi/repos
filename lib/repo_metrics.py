"""Per-repository metric fetchers: issue resolution time, languages, latest version."""

import json
import logging
import time
from urllib.parse import quote as url_quote

from lib.github_api import (
    DEFAULT_PAGE_SIZE,
    GITHUB_API_BASE_URL,
    make_github_request,
)
from lib.utils import get_human_readable_time, parse_github_datetime


def get_average_issue_resolution_time(repo_full_name, headers, console):
    """Calculate the average time to resolve issues for a single repository."""
    issues_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/issues"
    total_resolution_seconds = 0.0
    closed_issue_count = 0
    page = 1
    processed_any_pages = False

    logging.info(f"Calculating avg issue resolution time for {repo_full_name}...")

    while True:
        params = {'state': 'closed', 'page': page, 'per_page': DEFAULT_PAGE_SIZE}
        response = make_github_request(issues_url, headers, params=params, console=console)

        if response is None:
            logging.warning(f"Could not retrieve closed issues page {page} for {repo_full_name}. Stopping calculation.")
            if not processed_any_pages:
                return None
            return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else 0.0

        processed_any_pages = True
        try:
            issues = response.json()
            if not isinstance(issues, list):
                logging.error(f"Unexpected JSON response type for issues of {repo_full_name} (page {page}): {type(issues)}")
                return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else 0.0
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON response for closed issues of {repo_full_name}, page {page}.")
            return total_resolution_seconds / closed_issue_count if closed_issue_count > 0 else 0.0

        if not issues:
            logging.debug(f"No more issues found on page {page} for {repo_full_name}.")
            break

        valid_issues_on_page = 0
        for issue in issues:
            if isinstance(issue, dict) and 'pull_request' not in issue and issue.get('created_at') and issue.get('closed_at'):
                created_at = parse_github_datetime(issue['created_at'])
                closed_at = parse_github_datetime(issue['closed_at'])

                if created_at and closed_at:
                    if closed_at >= created_at:
                        resolution_time = (closed_at - created_at).total_seconds()
                        total_resolution_seconds += resolution_time
                        closed_issue_count += 1
                        valid_issues_on_page += 1
                    else:
                        logging.info(f"Issue #{issue.get('number')} in {repo_full_name} closed at {closed_at} before creation at {created_at}. Skipping.")
            elif not isinstance(issue, dict):
                logging.warning(f"Unexpected item type in issues list for {repo_full_name}: {type(issue)}")

        logging.debug(f"Processed page {page} for {repo_full_name}, found {len(issues)} items, {valid_issues_on_page} valid closed issues.")

        if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
            page += 1
            time.sleep(0.1)
        else:
            logging.debug(f"No 'next' link found on page {page} for {repo_full_name}. Assuming last page.")
            break

    if closed_issue_count > 0:
        average_seconds = total_resolution_seconds / closed_issue_count
        logging.info(f"Calculated average resolution time for {repo_full_name}: {average_seconds:.2f} seconds over {closed_issue_count} issues.")
        return average_seconds

    logging.info(f"No valid closed issues found for {repo_full_name} to calculate average resolution time.")
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


def get_latest_version_info(repo_full_name, headers, console=None):
    """Return latest version info from releases or tags for a repository.

    Tries the latest release first. If none, falls back to the latest tag.
    Includes a short rationale (release body or commit message subject).
    Returns a dict with keys: type, name, url, date_api, date_str, rationale.
    """
    base_api = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}"

    release_url = f"{base_api}/releases/latest"
    rel_resp = make_github_request(release_url, headers, console=console)
    if rel_resp and rel_resp.status_code == 200:
        try:
            rel = rel_resp.json()
            tag_name = rel.get('tag_name') or rel.get('name') or 'unknown'
            html_url = rel.get('html_url') or f"https://github.com/{repo_full_name}/releases"
            published_at = parse_github_datetime(rel.get('published_at'))
            rationale_raw = rel.get('name') or ''
            if not rationale_raw:
                rationale_raw = (rel.get('body') or '').strip()
            rationale = (rationale_raw or '').splitlines()[0][:120] if rationale_raw else ''
            return {
                'type': 'release',
                'name': tag_name,
                'url': html_url,
                'date_api': published_at,
                'date_str': get_human_readable_time(published_at) if published_at else 'Unknown',
                'rationale': rationale
            }
        except Exception as e:
            logging.warning(f"Failed parsing latest release for {repo_full_name}: {e}")

    tags_url = f"{base_api}/tags"
    tags_resp = make_github_request(tags_url, headers, params={'per_page': 1}, console=console)
    if tags_resp and tags_resp.status_code == 200:
        try:
            tags = tags_resp.json()
            if isinstance(tags, list) and tags:
                tag = tags[0]
                tag_name = tag.get('name') or 'unknown'
                commit_sha = ((tag.get('commit') or {}).get('sha'))
                commit_date = None
                rationale = ''
                if commit_sha:
                    commit_url = f"{base_api}/commits/{commit_sha}"
                    commit_resp = make_github_request(commit_url, headers, console=console)
                    if commit_resp and commit_resp.status_code == 200:
                        try:
                            c = commit_resp.json()
                            info = (c.get('commit') or {})
                            date_str = (info.get('committer') or {}).get('date') or (info.get('author') or {}).get('date')
                            commit_date = parse_github_datetime(date_str)
                            msg = (info.get('message') or '').strip()
                            rationale = msg.splitlines()[0][:120] if msg else ''
                        except Exception as e:
                            logging.warning(f"Failed parsing commit {commit_sha} for {repo_full_name}: {e}")
                tag_url = f"https://github.com/{repo_full_name}/tree/{url_quote(tag_name)}"
                return {
                    'type': 'tag',
                    'name': tag_name,
                    'url': tag_url,
                    'date_api': commit_date,
                    'date_str': get_human_readable_time(commit_date) if commit_date else 'Unknown',
                    'rationale': rationale
                }
        except Exception as e:
            logging.warning(f"Failed parsing tags for {repo_full_name}: {e}")

    return {
        'type': None,
        'name': None,
        'url': None,
        'date_api': None,
        'date_str': 'Unknown',
        'rationale': ''
    }
