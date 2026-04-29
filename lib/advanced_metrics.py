"""Advanced repository signals: momentum, issue health, bus factor, recent commits, top contributors."""

import datetime
import logging

from lib.github_api import GITHUB_API_BASE_URL, make_github_request
from lib.utils import get_human_readable_time, parse_github_datetime


def calculate_momentum_score(repo_full_name, current_stars, headers, console=None):
    """Calculate repository momentum based on recent star growth.

    Returns dict with: score (0-100), stars_7d, stars_30d, trend.
    """
    try:
        stargazers_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/stargazers"
        params = {'per_page': 100}
        headers_with_accept = headers.copy()
        headers_with_accept['Accept'] = 'application/vnd.github.v3.star+json'

        response = make_github_request(stargazers_url, headers_with_accept, params=params, console=console)

        if not response or response.status_code != 200:
            return {'score': 0, 'stars_7d': 0, 'stars_30d': 0, 'trend': 'stable'}

        stargazers = response.json()
        if not isinstance(stargazers, list):
            return {'score': 0, 'stars_7d': 0, 'stars_30d': 0, 'trend': 'stable'}

        now = datetime.datetime.now(datetime.timezone.utc)
        seven_days_ago = now - datetime.timedelta(days=7)
        thirty_days_ago = now - datetime.timedelta(days=30)

        stars_7d = 0
        stars_30d = 0

        for star in stargazers:
            starred_at = parse_github_datetime(star.get('starred_at'))
            if not starred_at:
                continue

            if starred_at >= seven_days_ago:
                stars_7d += 1
                stars_30d += 1
            elif starred_at >= thirty_days_ago:
                stars_30d += 1

        weekly_rate = stars_7d / 7.0
        monthly_rate = stars_30d / 30.0

        acceleration = max(0, (weekly_rate - monthly_rate) * 10)
        base_score = min(50, stars_7d * 2)
        size_factor = min(30, (current_stars / 100) * 0.5)
        score = min(100, base_score + acceleration + size_factor)

        if stars_7d > 5:
            trend = 'rising'
        elif stars_7d > 0:
            trend = 'growing'
        else:
            trend = 'stable'

        return {
            'score': round(score, 1),
            'stars_7d': stars_7d,
            'stars_30d': stars_30d,
            'trend': trend
        }

    except Exception as e:
        logging.warning(f"Error calculating momentum for {repo_full_name}: {e}")
        return {'score': 0, 'stars_7d': 0, 'stars_30d': 0, 'trend': 'stable'}


def calculate_issue_health(repo_full_name, open_issues_count, avg_resolution_time, headers, console=None):
    """Calculate issue health score based on response time and stale issues.

    Returns dict with: health_score (0-100), status, avg_response_hours, stale_issues_count.
    """
    try:
        if open_issues_count == 0:
            return {
                'health_score': 100,
                'status': 'healthy',
                'avg_response_hours': 0,
                'stale_issues_count': 0
            }

        issues_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/issues"
        params = {'state': 'open', 'per_page': 30, 'sort': 'created', 'direction': 'desc'}
        response = make_github_request(issues_url, headers, params=params, console=console)

        if not response or response.status_code != 200:
            return {
                'health_score': 50,
                'status': 'unknown',
                'avg_response_hours': 0,
                'stale_issues_count': 0
            }

        issues = response.json()
        if not isinstance(issues, list):
            return {
                'health_score': 50,
                'status': 'unknown',
                'avg_response_hours': 0,
                'stale_issues_count': 0
            }

        now = datetime.datetime.now(datetime.timezone.utc)
        ninety_days_ago = now - datetime.timedelta(days=90)

        response_times = []
        stale_count = 0

        for issue in issues:
            created_at = parse_github_datetime(issue.get('created_at'))
            updated_at = parse_github_datetime(issue.get('updated_at'))

            if not created_at:
                continue

            if updated_at and updated_at < ninety_days_ago:
                stale_count += 1

            if created_at and updated_at and created_at != updated_at:
                response_time = (updated_at - created_at).total_seconds() / 3600
                response_times.append(response_time)

        avg_response_hours = sum(response_times) / len(response_times) if response_times else 0

        score = 100

        if avg_response_hours > 168:
            score -= 40
        elif avg_response_hours > 48:
            score -= 20

        stale_ratio = stale_count / len(issues) if issues else 0
        score -= stale_ratio * 30

        if avg_resolution_time and avg_resolution_time > 0:
            resolution_days = avg_resolution_time / (24 * 3600)
            if resolution_days > 30:
                score -= 10

        score = max(0, min(100, score))

        if score >= 80:
            status = 'healthy'
        elif score >= 50:
            status = 'moderate'
        else:
            status = 'needs_attention'

        return {
            'health_score': round(score, 1),
            'status': status,
            'avg_response_hours': round(avg_response_hours, 1),
            'stale_issues_count': stale_count
        }

    except Exception as e:
        logging.warning(f"Error calculating issue health for {repo_full_name}: {e}")
        return {
            'health_score': 50,
            'status': 'unknown',
            'avg_response_hours': 0,
            'stale_issues_count': 0
        }


def calculate_bus_factor(contributors_count):
    """Estimate bus factor (risk if key contributors leave).

    Returns dict with: bus_factor (int), risk_level.
    """
    if contributors_count is None or contributors_count == 0:
        return {'bus_factor': 0, 'risk_level': 'unknown'}

    bus_factor = max(1, min(5, contributors_count // 2))

    if bus_factor == 1:
        risk_level = 'critical'
    elif bus_factor == 2:
        risk_level = 'moderate'
    else:
        risk_level = 'healthy'

    return {
        'bus_factor': bus_factor,
        'risk_level': risk_level
    }


def fetch_recent_commits(repo_full_name, headers, console=None, count=5):
    """Fetch recent commits for repository detail modal."""
    try:
        commits_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/commits"
        params = {'per_page': count}
        response = make_github_request(commits_url, headers, params=params, console=console)

        if not response or response.status_code != 200:
            return []

        commits = response.json()
        if not isinstance(commits, list):
            return []

        result = []
        for commit in commits:
            commit_data = commit.get('commit', {})
            result.append({
                'sha': commit.get('sha', '')[:7],
                'message': commit_data.get('message', '').split('\n')[0][:100],
                'author': commit_data.get('author', {}).get('name', 'Unknown'),
                'date': get_human_readable_time(parse_github_datetime(
                    commit_data.get('author', {}).get('date')
                )),
                'url': commit.get('html_url', '#')
            })

        return result

    except Exception as e:
        logging.warning(f"Error fetching recent commits for {repo_full_name}: {e}")
        return []


def fetch_top_contributors(repo_full_name, headers, console=None, count=5):
    """Fetch top contributors for repository detail modal."""
    try:
        contributors_url = f"{GITHUB_API_BASE_URL}/repos/{repo_full_name}/contributors"
        params = {'per_page': count, 'anon': 'false'}
        response = make_github_request(contributors_url, headers, params=params, console=console)

        if not response or response.status_code != 200:
            return []

        contributors = response.json()
        if not isinstance(contributors, list):
            return []

        result = []
        for contrib in contributors:
            result.append({
                'login': contrib.get('login', 'Unknown'),
                'avatar_url': contrib.get('avatar_url', ''),
                'contributions': contrib.get('contributions', 0),
                'profile_url': contrib.get('html_url', '#')
            })

        return result

    except Exception as e:
        logging.warning(f"Error fetching top contributors for {repo_full_name}: {e}")
        return []
