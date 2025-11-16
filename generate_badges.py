#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Repository Badge Generator
Generates custom SVG badges and statistics for README and dashboard
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple


class BadgeGenerator:
    """Generate beautiful SVG badges for GitHub stats"""
    
    # Color schemes
    COLORS = {
        'blue': '#007ec6',
        'green': '#44cc11',
        'yellow': '#dfb317',
        'orange': '#fe7d37',
        'red': '#e05d44',
        'purple': '#9f5dc9',
        'pink': '#ff69b4',
        'gray': '#555555',
        'lightgray': '#9f9f9f',
        'brightgreen': '#4c1',
    }
    
    def __init__(self, data_file: str = 'docs/repositories-data.json'):
        """Initialize with repository data"""
        with open(data_file, 'r', encoding='utf-8') as f:
            self.repositories = json.load(f)
        self.stats = self._calculate_stats()
    
    def _calculate_stats(self) -> Dict:
        """Calculate comprehensive statistics from repository data"""
        total_repos = len(self.repositories)
        total_stars = sum(repo.get('stars', 0) or 0 for repo in self.repositories)
        total_forks = sum(repo.get('forks', 0) or 0 for repo in self.repositories)
        total_watchers = sum(repo.get('watchers', 0) or 0 for repo in self.repositories)
        total_issues = sum(repo.get('open_issues_count', 0) or 0 for repo in self.repositories)
        
        # Advanced metrics
        total_commits = sum(repo.get('commits', 0) or 0 for repo in self.repositories)
        total_contributors = sum(repo.get('contributors', 0) or 0 for repo in self.repositories)
        total_closed_issues = sum(repo.get('closed_issues_count', 0) or 0 for repo in self.repositories)
        
        # Calculate resolved issues
        total_all_issues = total_issues + total_closed_issues
        issues_resolved = total_closed_issues
        issue_resolution_rate = (issues_resolved / total_all_issues * 100) if total_all_issues > 0 else 0
        
        # Language statistics
        languages = {}
        for repo in self.repositories:
            if lang := repo.get('language'):
                languages[lang] = languages.get(lang, 0) + 1
        
        # Top repository by stars
        top_repo = max(self.repositories, key=lambda x: x.get('stars', 0), default={})
        
        # Activity metrics
        active_repos = [r for r in self.repositories if not r.get('archived', False)]
        avg_stars = total_stars / total_repos if total_repos > 0 else 0
        avg_commits = total_commits / total_repos if total_repos > 0 else 0
        
        # Fork analysis
        original_repos = [r for r in self.repositories if not r.get('fork', False)]
        forked_repos = [r for r in self.repositories if r.get('fork', False)]
        
        # Repository with most commits
        most_active_repo = max(self.repositories, key=lambda x: x.get('commits', 0), default={})
        
        # Repository with most contributors
        most_collaborative_repo = max(self.repositories, key=lambda x: x.get('contributors', 0), default={})
        
        return {
            'total_repos': total_repos,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'total_watchers': total_watchers,
            'total_issues': total_issues,
            'total_commits': total_commits,
            'total_contributors': total_contributors,
            'total_closed_issues': total_closed_issues,
            'total_all_issues': total_all_issues,
            'issues_resolved': issues_resolved,
            'issue_resolution_rate': round(issue_resolution_rate, 1),
            'languages': languages,
            'top_language': max(languages.items(), key=lambda x: x[1])[0] if languages else 'N/A',
            'top_repo': top_repo.get('name', 'N/A'),
            'top_repo_stars': top_repo.get('stars', 0),
            'active_repos': len(active_repos),
            'archived_repos': total_repos - len(active_repos),
            'avg_stars': round(avg_stars, 1),
            'avg_commits': round(avg_commits, 1),
            'original_repos': len(original_repos),
            'forked_repos': len(forked_repos),
            'most_active_repo': most_active_repo.get('name', 'N/A'),
            'most_active_commits': most_active_repo.get('commits', 0),
            'most_collaborative_repo': most_collaborative_repo.get('name', 'N/A'),
            'most_collaborative_contributors': most_collaborative_repo.get('contributors', 0),
        }
    
    def _create_svg_badge(self, label: str, value: str, color: str = 'blue') -> str:
        """Create a single SVG badge"""
        # Calculate widths based on text length
        label_width = len(label) * 7 + 10
        value_width = len(str(value)) * 7 + 10
        total_width = label_width + value_width
        
        color_hex = self.COLORS.get(color, color)
        
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <rect width="{label_width}" height="20" fill="#555"/>
        <rect x="{label_width}" width="{value_width}" height="20" fill="{color_hex}"/>
        <rect width="{total_width}" height="20" fill="url(#b)"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="{label_width/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
        <text x="{label_width/2}" y="14">{label}</text>
        <text x="{label_width + value_width/2}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
        <text x="{label_width + value_width/2}" y="14">{value}</text>
    </g>
</svg>'''
        return svg
    
    def generate_all_badges(self, output_dir: str = 'docs/badges') -> None:
        """Generate all badge files"""
        os.makedirs(output_dir, exist_ok=True)
        
        badges = [
            ('total_repos', 'Total Repos', str(self.stats['total_repos']), 'blue'),
            ('total_stars', 'Total Stars', f"⭐ {self.stats['total_stars']}", 'yellow'),
            ('total_forks', 'Total Forks', f"🍴 {self.stats['total_forks']}", 'green'),
            ('total_watchers', 'Total Watchers', f"👀 {self.stats['total_watchers']}", 'blue'),
            ('total_commits', 'Total Commits', f"💾 {self.stats['total_commits']:,}", 'purple'),
            ('total_contributors', 'Contributors', f"👥 {self.stats['total_contributors']}", 'brightgreen'),
            ('issues_resolved', 'Issues Resolved', f"✅ {self.stats['issues_resolved']}", 'green'),
            ('issue_resolution_rate', 'Resolution Rate', f"{self.stats['issue_resolution_rate']}%", 'brightgreen'),
            ('active_repos', 'Active Repos', f"🚀 {self.stats['active_repos']}", 'green'),
            ('languages', 'Languages', str(len(self.stats['languages'])), 'purple'),
            ('top_language', 'Top Language', self.stats['top_language'], 'orange'),
            ('top_repo', 'Top Repo', f"{self.stats['top_repo']} ({self.stats['top_repo_stars']}★)", 'brightgreen'),
            ('active_repos', 'Active', str(self.stats['active_repos']), 'green'),
            ('avg_stars', 'Avg Stars', str(self.stats['avg_stars']), 'yellow'),
            ('avg_commits', 'Avg Commits', str(self.stats['avg_commits']), 'purple'),
        ]
        
        for filename, label, value, color in badges:
            svg_content = self._create_svg_badge(label, value, color)
            with open(f"{output_dir}/{filename}.svg", 'w', encoding='utf-8') as f:
                f.write(svg_content)
        
        print(f"✅ Generated {len(badges)} badges in {output_dir}/")
    
    def generate_stats_markdown(self, output_file: str = 'docs/STATS.md') -> None:
        """Generate detailed statistics in Markdown format"""
        md_content = f"""# 📊 Repository Statistics

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 📈 Overview

| Metric | Value |
|--------|-------|
| 📦 Total Repositories | **{self.stats['total_repos']}** |
| ⭐ Total Stars | **{self.stats['total_stars']:,}** |
| 🍴 Total Forks | **{self.stats['total_forks']:,}** |
| 👀 Total Watchers | **{self.stats['total_watchers']:,}** |
| 💾 Total Commits | **{self.stats['total_commits']:,}** |
| 👥 Total Contributors | **{self.stats['total_contributors']:,}** |
| ❗ Open Issues | **{self.stats['total_issues']}** |
| ✅ Closed Issues | **{self.stats['total_closed_issues']}** |
| 💻 Languages Used | **{len(self.stats['languages'])}** |

---

## 🏆 Top Performers

### Most Starred Repository
**{self.stats['top_repo']}** - ⭐ {self.stats['top_repo_stars']:,} stars

### Most Active Repository (by commits)
**{self.stats['most_active_repo']}** - 💾 {self.stats['most_active_commits']:,} commits

### Most Collaborative Repository
**{self.stats['most_collaborative_repo']}** - 👥 {self.stats['most_collaborative_contributors']} contributors

### Most Used Language
**{self.stats['top_language']}** - Used in {self.stats['languages'][self.stats['top_language']]} repositories

---

## 📊 Repository Breakdown

| Category | Count | Percentage |
|----------|-------|------------|
| 🎯 Original Repositories | {self.stats['original_repos']} | {self.stats['original_repos']/self.stats['total_repos']*100:.1f}% |
| 🍴 Forked Repositories | {self.stats['forked_repos']} | {self.stats['forked_repos']/self.stats['total_repos']*100:.1f}% |
| ✅ Active Repositories | {self.stats['active_repos']} | {self.stats['active_repos']/self.stats['total_repos']*100:.1f}% |
| 📦 Archived Repositories | {self.stats['archived_repos']} | {self.stats['archived_repos']/self.stats['total_repos']*100:.1f}% |

---

## 🎯 Development Activity

| Metric | Value |
|--------|-------|
| 💾 Average Commits per Repository | **{self.stats['avg_commits']:.1f}** |
| ⭐ Average Stars per Repository | **{self.stats['avg_stars']:.1f}** |
| ✅ Issue Resolution Rate | **{self.stats['issue_resolution_rate']:.1f}%** |
| 📝 Total Issues (Open + Closed) | **{self.stats['total_all_issues']}** |
| ✅ Issues Resolved | **{self.stats['issues_resolved']}** |

---

## 💻 Language Distribution

"""
        # Sort languages by count
        sorted_langs = sorted(self.stats['languages'].items(), key=lambda x: x[1], reverse=True)
        
        md_content += "| Language | Repositories | Percentage |\n"
        md_content += "|----------|--------------|------------|\n"
        
        for lang, count in sorted_langs[:10]:  # Top 10 languages
            percentage = count / self.stats['total_repos'] * 100
            bar = '█' * int(percentage / 5)  # Visual bar
            md_content += f"| {lang} | {count} | {bar} {percentage:.1f}% |\n"
        
        md_content += f"""
---

## 📅 Activity Metrics

- **Average Stars per Repository**: {self.stats['avg_stars']}
- **Active Repositories**: {self.stats['active_repos']} ({self.stats['active_repos']/self.stats['total_repos']*100:.1f}%)
- **Total Issues to Resolve**: {self.stats['total_issues']}

---

## 🎯 Engagement Score

"""
        engagement_score = (
            self.stats['total_stars'] * 1.0 +
            self.stats['total_forks'] * 2.0 +
            self.stats['total_watchers'] * 0.5
        ) / self.stats['total_repos']
        
        md_content += f"**Overall Engagement Score**: {engagement_score:.2f}/repository\n\n"
        md_content += f"This score is calculated based on stars, forks, and watchers across all repositories.\n\n"
        
        md_content += """---

*These statistics are automatically generated from GitHub repository data.*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Generated statistics markdown: {output_file}")
    
    def generate_json_summary(self, output_file: str = 'docs/stats-summary.json') -> None:
        """Generate a JSON summary for easy consumption"""
        summary = {
            'generated_at': datetime.now().isoformat(),
            'overview': {
                'total_repositories': self.stats['total_repos'],
                'total_stars': self.stats['total_stars'],
                'total_forks': self.stats['total_forks'],
                'total_watchers': self.stats['total_watchers'],
                'total_issues': self.stats['total_issues'],
                'total_commits': self.stats['total_commits'],
                'total_contributors': self.stats['total_contributors'],
                'total_closed_issues': self.stats['total_closed_issues'],
                'total_all_issues': self.stats['total_all_issues'],
            },
            'development_activity': {
                'total_commits': self.stats['total_commits'],
                'average_commits_per_repo': self.stats['avg_commits'],
                'total_contributors': self.stats['total_contributors'],
                'issues_resolved': self.stats['issues_resolved'],
                'issue_resolution_rate': self.stats['issue_resolution_rate'],
            },
            'languages': {
                'count': len(self.stats['languages']),
                'top_language': self.stats['top_language'],
                'distribution': self.stats['languages'],
            },
            'top_performers': {
                'most_starred': {
                    'name': self.stats['top_repo'],
                    'stars': self.stats['top_repo_stars'],
                },
                'most_active': {
                    'name': self.stats['most_active_repo'],
                    'commits': self.stats['most_active_commits'],
                },
                'most_collaborative': {
                    'name': self.stats['most_collaborative_repo'],
                    'contributors': self.stats['most_collaborative_contributors'],
                },
            },
            'breakdown': {
                'original': self.stats['original_repos'],
                'forked': self.stats['forked_repos'],
                'active': self.stats['active_repos'],
                'archived': self.stats['archived_repos'],
            },
            'metrics': {
                'average_stars': self.stats['avg_stars'],
                'average_commits': self.stats['avg_commits'],
                'issue_resolution_rate': self.stats['issue_resolution_rate'],
                'engagement_score': round((
                    self.stats['total_stars'] * 1.0 +
                    self.stats['total_forks'] * 2.0 +
                    self.stats['total_watchers'] * 0.5
                ) / max(self.stats['total_repos'], 1), 2)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Generated JSON summary: {output_file}")


def main():
    """Main execution function"""
    print("🚀 GitHub Badge & Stats Generator\n")
    
    try:
        generator = BadgeGenerator()
        
        # Generate badges
        print("📛 Generating badges...")
        generator.generate_all_badges()
        
        # Generate statistics markdown
        print("\n📄 Generating statistics markdown...")
        generator.generate_stats_markdown()
        
        # Generate JSON summary
        print("\n🗂️  Generating JSON summary...")
        generator.generate_json_summary()
        
        print("\n✅ All assets generated successfully!")
        print("\n📊 Statistics Summary:")
        print(f"   • Total Repositories: {generator.stats['total_repos']}")
        print(f"   • Total Stars: {generator.stats['total_stars']:,}")
        print(f"   • Total Forks: {generator.stats['total_forks']:,}")
        print(f"   • Languages: {len(generator.stats['languages'])}")
        print(f"   • Top Language: {generator.stats['top_language']}")
        print(f"   • Top Repo: {generator.stats['top_repo']} ({generator.stats['top_repo_stars']}★)")
        
    except FileNotFoundError:
        print("❌ Error: repositories-data.json not found!")
        print("   Please run stats.py first to generate repository data.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
