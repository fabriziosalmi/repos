#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README Badge Updater
Automatically updates the statistics badges in README.md
"""

import json
import re
from datetime import datetime


def load_stats_summary(file_path: str = 'docs/stats-summary.json') -> dict:
    """Load the stats summary JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_readme_badges(readme_path: str = 'README.md') -> None:
    """Update badges in README.md with current statistics"""
    
    # Load current stats
    stats = load_stats_summary()
    
    # Read README content
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract values with safe defaults to avoid KeyError
    overview = stats.get('overview', {})
    dev_activity = stats.get('development_activity', {})
    languages = stats.get('languages', {})
    breakdown = stats.get('breakdown', {})
    top_performers = stats.get('top_performers', {})
    metrics = stats.get('metrics', {})
    
    total_repos = overview.get('total_repositories', 0)
    total_stars = f"{overview.get('total_stars', 0):,}"
    total_forks = overview.get('total_forks', 0)
    total_commits = f"{overview.get('total_commits', 0):,}"
    total_contributors = overview.get('total_contributors', 0)
    issues_resolved = dev_activity.get('issues_resolved', 0)
    resolution_rate = dev_activity.get('issue_resolution_rate', 0)
    languages_count = languages.get('count', 0)
    top_language = languages.get('top_language', 'N/A')
    active_repos = breakdown.get('active', 0)
    most_starred = top_performers.get('most_starred', {})
    top_repo_name = most_starred.get('name', 'N/A')
    top_repo_stars = most_starred.get('stars', 0)
    avg_stars = metrics.get('average_stars', 0)
    avg_commits = metrics.get('average_commits', 0)
    
    # Find most used language count
    lang_dist = languages.get('distribution', {})
    top_lang_count = lang_dist.get(top_language, 0)
    
    # Create new badges section
    new_badges = f"""<div align="center">

![Total Repos](https://img.shields.io/badge/Total_Repos-{total_repos}-blue?style=flat-square)
![Total Stars](https://img.shields.io/badge/Total_Stars-{total_stars}-yellow?style=flat-square)
![Total Forks](https://img.shields.io/badge/Total_Forks-{total_forks}-green?style=flat-square)
![Total Commits](https://img.shields.io/badge/Total_Commits-{total_commits}-purple?style=flat-square)
![Contributors](https://img.shields.io/badge/Contributors-{total_contributors}-brightgreen?style=flat-square)
![Issues Resolved](https://img.shields.io/badge/Issues_Resolved-{issues_resolved}-green?style=flat-square)
![Resolution Rate](https://img.shields.io/badge/Resolution_Rate-{resolution_rate}%25-brightgreen?style=flat-square)

**🏆 Most Starred: {top_repo_name} ({top_repo_stars} ⭐) | 💻 Top Language: {top_language} ({top_lang_count} repos) | 📊 Avg: {avg_stars}★ / {avg_commits} commits**

</div>"""
    
    # Pattern to match the stats section
    pattern = r'## 📈 Live Statistics\s*\n\s*<div align="center">.*?</div>'
    
    replacement = f'## 📈 Live Statistics\n\n{new_badges}'
    
    # Replace in content
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write back to README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ README.md badges updated successfully!")
    print(f"\n📊 Current Stats:")
    print(f"   • Repositories: {total_repos}")
    print(f"   • Stars: {total_stars}")
    print(f"   • Forks: {total_forks}")
    print(f"   • Languages: {languages_count}")
    print(f"   • Top Repo: {top_repo_name} ({top_repo_stars}★)")


def main():
    """Main execution"""
    try:
        print("🔄 Updating README badges...\n")
        update_readme_badges()
        print(f"\n⏰ Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        print("   Make sure to run generate_badges.py first!")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
