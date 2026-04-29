"""Output writers: JSON dump and Markdown report generation."""

import datetime
import json
import logging
from urllib.parse import quote as url_quote

from lib.utils import get_repository_status_indicator


def save_to_json(data, filename="github_stats.json"):
    """Save the given data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            def dt_converter(o):
                if isinstance(o, datetime.datetime):
                    return o.isoformat()
                try:
                    json.dumps(o)
                    return o
                except TypeError:
                    return str(o)

            json.dump(data, f, indent=4, default=dt_converter, ensure_ascii=False)
        logging.info(f"Data successfully saved to {filename}")
        print(f"Data saved to {filename}")
    except (IOError, TypeError) as e:
        logging.error(f"Error saving data to JSON file '{filename}': {e}")
        print(f"Error saving to JSON: {e}")


def create_markdown_table(repositories, total_stars, top_repo_full_names, username, filename="github_stats.md"):
    """Create a Markdown file with summary, chart, and detailed table."""
    logging.info(f"Generating Markdown report '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# GitHub Repository Stats for {username}\n\n")
            f.write(f"Total stars across owned repositories scanned: **{total_stars:,}** ⭐\n\n")

            f.write(f"## Overall Stats\n\n")
            stats_card_url = f"https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=github_dark&hide_border=true&cache_seconds=3600"
            streak = f"https://streak-stats.demolab.com/?user={username}"
            trophy = f"https://github-profile-trophy.vercel.app/?username={username}"
            f.write(f"![{username}'s GitHub stats]({stats_card_url})\n\n")
            f.write(f"![{username}'s GitHub streak]({streak})\n\n")
            f.write(f"![{username}'s GitHub trophy]({trophy})\n\n")

            if top_repo_full_names:
                num_chart_repos = min(len(top_repo_full_names), 10)
                chart_repo_names = top_repo_full_names[:num_chart_repos]
                f.write(f"## Star History (Top {num_chart_repos} Repositories by Stars)\n\n")
                repo_list_param = ",".join(url_quote(name) for name in chart_repo_names)
                chart_url = f"https://api.star-history.com/svg?repos={repo_list_param}&type=Date&theme=dark"
                f.write(f"[![Star History Chart]({chart_url})](https://star-history.com/#{'&'.join(repo_list_param.split(','))}&Date)\n\n")
            else:
                f.write("*(Could not generate star history chart - no repositories found or an error occurred)*\n\n")

            f.write(f"## Repository Details\n\n")
            f.write("| Repository | Description | Language 💻 | Version 🏷️ | Released 📅 | Stars ⭐ | Forks 🍴 | Watchers 👀 | Commits 💾 | Contributors 👥 | Issues ✅ | Last Update 🕒 | Status 📊 | Notes 📝 |\n")
            f.write("|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|\n")

            for repo in repositories:
                description = repo.get('description', 'No description')
                description = description.replace("|", "\\|")
                description = description.replace("\n", "<br>")

                if len(description) > 50:
                    description = description[:47] + "..."

                language = repo.get('language', 'N/A')
                if language == 'Not specified':
                    language = 'N/A'

                status_text = get_repository_status_indicator(repo)

                stars_str = f"{repo.get('stars', 0):,}"
                forks_str = f"{repo.get('forks', 0):,}"
                watchers_str = f"{repo.get('watchers', 0):,}"

                commits_val = repo.get('commits')
                commits_str = f"{commits_val:,}" if commits_val is not None else "N/A"

                contrib_val = repo.get('contributors')
                contrib_str = f"{contrib_val:,}" if contrib_val is not None else "N/A"

                issues_val = repo.get('closed_issues_count')
                issues_str = f"{issues_val:,}" if issues_val is not None else "N/A"

                last_update_str = repo.get('last_update_str', "Unknown")

                ver_name = repo.get('version') or '—'
                ver_url = repo.get('latest_version_url') or ''
                ver_date = repo.get('latest_version_date_str', 'Unknown')
                note = repo.get('latest_version_rationale') or ''
                if len(note) > 80:
                    note = note[:77] + '...'

                repo_name_sanitized = repo.get('name', 'N/A').replace('[', '\\[').replace(']', '\\]')
                repo_url = repo.get('url', '#')

                if ver_url and ver_name != '—':
                    ver_cell = f"[{ver_name}]({ver_url})"
                else:
                    ver_cell = ver_name

                f.write(f"| [{repo_name_sanitized}]({repo_url}) "
                        f"| {description} "
                        f"| {language} "
                        f"| {ver_cell} "
                        f"| {ver_date} "
                        f"| {stars_str} "
                        f"| {forks_str} "
                        f"| {watchers_str} "
                        f"| {commits_str} "
                        f"| {contrib_str} "
                        f"| {issues_str} "
                        f"| {last_update_str} "
                        f"| {status_text} "
                        f"| {note} |\n")

        logging.info(f"Markdown report saved to {filename}")
        print(f"Markdown report saved to {filename}")

    except IOError as e:
        logging.error(f"Error writing Markdown file '{filename}': {e}")
        print(f"Error creating Markdown file: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during Markdown generation: {e}", exc_info=True)
        print(f"An unexpected error occurred creating Markdown file: {e}")
