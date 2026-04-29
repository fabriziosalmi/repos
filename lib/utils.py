"""Pure utility functions: datetime parsing, formatting, validation, file I/O, insights."""

import datetime
import logging
import os
import shutil


def validate_data_completeness(repositories, total_stars):
    """Validate that the collected data is complete and not corrupted."""
    if not repositories or not isinstance(repositories, list):
        return False, "No repositories found or invalid data format"

    if total_stars < 0:
        return False, "Invalid total stars count"

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
        if os.path.exists(filename):
            shutil.copy2(filename, backup_file)
            logging.info(f"Created backup: {backup_file}")

        try:
            write_func()

            if not os.path.exists(filename):
                raise IOError(f"Write function did not create the expected file: {filename}")

        except Exception as write_error:
            logging.error(f"Error during write operation: {write_error}")
            raise

        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            raise IOError("Output file is empty or doesn't exist")

        logging.info(f"Successfully wrote {filename}")

        if os.path.exists(backup_file):
            os.remove(backup_file)

        return True

    except Exception as e:
        logging.error(f"Error writing {filename}: {e}")

        if os.path.exists(backup_file):
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                shutil.move(backup_file, filename)
                logging.info(f"Restored {filename} from backup")
            except Exception as restore_error:
                logging.error(f"Failed to restore backup: {restore_error}")

        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

        return False


def get_human_readable_time(timestamp):
    """Convert a timezone-aware datetime to a human-readable time difference."""
    if not isinstance(timestamp, datetime.datetime):
        logging.warning(f"Invalid timestamp type received: {type(timestamp)}. Returning 'Unknown'.")
        return "Unknown"
    if timestamp.tzinfo is None:
        logging.warning("Timestamp provided to get_human_readable_time is naive. Assuming UTC.")
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

    now = datetime.datetime.now(datetime.timezone.utc)
    time_diff = now - timestamp

    seconds = time_diff.total_seconds()
    days = time_diff.days

    if seconds < 0:
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
    elif days < 30:
        return f"{int(days // 7)} weeks ago"
    elif days < 365:
        return f"{int(days // 30)} months ago"
    else:
        return f"{int(days // 365)} years ago"


def parse_github_datetime(datetime_str):
    """Safely parses GitHub's ISO 8601 datetime strings."""
    if not datetime_str:
        return None
    try:
        return datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except (ValueError, TypeError) as e:
        logging.warning(f"Could not parse datetime string '{datetime_str}': {e}")
        return None


def format_resolution_time(seconds):
    """Format resolution time in seconds into a human-readable string (d, h, m, s)."""
    if seconds is None:
        return "N/A"
    if not isinstance(seconds, (int, float)):
        logging.warning(f"Invalid type ({type(seconds)}) passed to format_resolution_time.")
        return "Error"

    if seconds < 0:
        logging.warning(f"Negative resolution time ({seconds}s) passed to formatter.")
        return "Invalid Data"

    if abs(seconds) < 0.001:
        return "No Closed Issues"

    seconds = float(seconds)

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, sec = divmod(remainder, 60)

    parts = []
    if days >= 1:
        parts.append(f"{int(days)}d")
    if hours >= 1:
        parts.append(f"{int(hours)}h")
    if minutes >= 1:
        parts.append(f"{int(minutes)}m")
    if sec > 0.1 or (not parts and seconds > 0):
        if days > 0 or hours > 0:
            parts.append(f"{int(sec)}s")
        elif seconds < 3600:
            parts.append(f"{sec:.1f}s")
        else:
            parts.append(f"{int(sec)}s")

    return " ".join(parts) if parts else "~0s"


def get_repository_status_indicator(repo):
    """Generate status indicator for repository based on various criteria."""
    if repo.get('archived', False):
        return "📦 ARCHIVED"

    if repo.get('disabled', False):
        return "🚫 DISABLED"

    if repo.get('fork', False):
        return "🍴 FORK"

    last_update = repo.get('last_update')
    if last_update:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            days_since_update = (now - last_update).days
            if days_since_update > 365:
                return "⚠️ INACTIVE"
            elif days_since_update > 180:
                return "⏰ STALE"
            elif days_since_update <= 7:
                return "🔥 ACTIVE"
        except Exception:
            pass

    if not repo.get('description') or repo.get('description') == "No description":
        return "📝 NO DESC"

    if repo.get('private', False):
        return "🔒 PRIVATE"

    return "✅ ACTIVE"


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
        if repo.get('archived', False):
            insights['archived_count'] += 1
        if repo.get('fork', False):
            insights['fork_count'] += 1

        language = repo.get('language', 'Unknown')
        if language and language != 'Not specified':
            insights['language_distribution'][language] = insights['language_distribution'].get(language, 0) + 1

        size = repo.get('size', 0)
        if size < 1000:
            insights['size_distribution']['small'] += 1
        elif size < 10000:
            insights['size_distribution']['medium'] += 1
        else:
            insights['size_distribution']['large'] += 1

        last_update = repo.get('last_update_api')
        if last_update:
            days_since_update = (now - last_update).days
            if days_since_update <= 30:
                insights['activity_distribution']['active'] += 1
            elif days_since_update <= 180:
                insights['activity_distribution']['stale'] += 1
            else:
                insights['activity_distribution']['inactive'] += 1

        created_at = repo.get('created_at_api')
        if created_at:
            days_old = (now - created_at).days
            if days_old <= 365:
                insights['repository_ages']['new'] += 1
            elif days_old <= 1825:
                insights['repository_ages']['mature'] += 1
            else:
                insights['repository_ages']['old'] += 1

        insights['total_watchers'] += repo.get('watchers', 0)
        insights['total_open_issues'] += repo.get('open_issues_count', 0)

    insights['top_languages'] = sorted(
        insights['language_distribution'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return insights
