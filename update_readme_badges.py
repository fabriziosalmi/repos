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
    
    # Extract values
    total_repos = stats['overview']['total_repositories']
    total_stars = f"{stats['overview']['total_stars']:,}"
    total_forks = stats['overview']['total_forks']
    languages_count = stats['languages']['count']
    top_language = stats['languages']['top_language']
    active_repos = stats['breakdown']['active']
    top_repo_name = stats['top_repository']['name']
    top_repo_stars = stats['top_repository']['stars']
    avg_stars = stats['metrics']['average_stars']
    
    # Find most used language count
    lang_dist = stats['languages']['distribution']
    top_lang_count = lang_dist.get(top_language, 0)
    
    # Create new badges section
    new_badges = f"""<div align="center">

![Total Repos](https://img.shields.io/badge/Total_Repos-{total_repos}-blue?style=flat-square)
![Total Stars](https://img.shields.io/badge/Total_Stars-{total_stars}-yellow?style=flat-square)
![Total Forks](https://img.shields.io/badge/Total_Forks-{total_forks}-green?style=flat-square)
![Languages](https://img.shields.io/badge/Languages-{languages_count}-purple?style=flat-square)
![Top Language](https://img.shields.io/badge/Top_Language-{top_language}-orange?style=flat-square)
![Active Repos](https://img.shields.io/badge/Active-{active_repos}-brightgreen?style=flat-square)

**🏆 Most Starred: {top_repo_name} ({top_repo_stars} ⭐) | 💻 Top Language: {top_language} ({top_lang_count} repos) | 📊 Avg Stars: {avg_stars}**

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
