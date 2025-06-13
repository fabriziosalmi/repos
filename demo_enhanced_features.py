#!/usr/bin/env python3
"""
Demonstration script for the enhanced GitHub Repository Stats functionality.
This script shows the new features working with sample data to avoid API rate limits.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add the parent directory to Python path so we can import stats
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stats import (
    get_repository_status_indicator,
    format_resolution_time,
    generate_repository_insights,
    safe_file_write
)

def create_sample_data():
    """Create comprehensive sample repository data demonstrating all features."""
    return [
        {
            "name": "caddy-waf",
            "full_name": "fabriziosalmi/caddy-waf", 
            "description": "Caddy WAF (Regex Rules, IP and DNS filtering, Rate Limiting, GeoIP, Tor, Anomaly Detection)",
            "url": "https://github.com/fabriziosalmi/caddy-waf",
            "stars": 521,
            "forks": 16,
            "watchers": 35,
            "commit_count": 584,
            "contributors_count": 4,
            "closed_issues_count": 1,
            "open_issues_count": 2,
            "language": "Go",
            "archived": False,
            "disabled": False,
            "private": False,  
            "fork": False,
            "license": "MIT License",
            "default_branch": "main",
            "size": 15420,
            "last_update_api": datetime(2024, 5, 15, 10, 0, 0, tzinfo=timezone.utc),
            "created_at_api": datetime(2022, 3, 10, 14, 30, 0, tzinfo=timezone.utc),
            "last_update_str": "1 months ago",
            "avg_issue_resolution_time": 1151978.5  # ~13 days in seconds
        },
        {
            "name": "patterns",
            "full_name": "fabriziosalmi/patterns",
            "description": "Automated OWASP CRS and Bad Bot Detection for Nginx, Apache, Traefik and HaProxy", 
            "url": "https://github.com/fabriziosalmi/patterns",
            "stars": 280,
            "forks": 5,
            "watchers": 12,
            "commit_count": 261,
            "contributors_count": 5,
            "closed_issues_count": 1,
            "open_issues_count": 0,
            "language": "Shell",
            "archived": False,
            "disabled": False,
            "private": False,
            "fork": False,
            "license": "Apache License 2.0",
            "default_branch": "main", 
            "size": 8950,
            "last_update_api": datetime(2024, 3, 20, 8, 45, 0, tzinfo=timezone.utc),
            "created_at_api": datetime(2021, 11, 5, 16, 20, 0, tzinfo=timezone.utc),
            "last_update_str": "3 months ago",
            "avg_issue_resolution_time": 573356.0  # ~6.6 days in seconds
        },
        {
            "name": "old-archived-project",
            "full_name": "fabriziosalmi/old-archived-project",
            "description": "An old project that has been archived",
            "url": "https://github.com/fabriziosalmi/old-archived-project",
            "stars": 15,
            "forks": 2,
            "watchers": 3,
            "commit_count": 45,
            "contributors_count": 1,
            "closed_issues_count": 0,
            "open_issues_count": 0,
            "language": "Python",
            "archived": True,  # Archived repository
            "disabled": False,
            "private": False,
            "fork": False,
            "license": "No license",
            "default_branch": "master",
            "size": 2340,
            "last_update_api": datetime(2022, 8, 10, 12, 0, 0, tzinfo=timezone.utc),
            "created_at_api": datetime(2020, 4, 1, 10, 15, 0, tzinfo=timezone.utc),
            "last_update_str": "2 years ago",
            "avg_issue_resolution_time": 0.0
        },
        {
            "name": "forked-utility",
            "full_name": "fabriziosalmi/forked-utility",
            "description": "A useful utility forked from another project",
            "url": "https://github.com/fabriziosalmi/forked-utility",
            "stars": 8,
            "forks": 0,
            "watchers": 1,
            "commit_count": 12,
            "contributors_count": 1,
            "closed_issues_count": 0,
            "open_issues_count": 1,
            "language": "JavaScript",
            "archived": False,
            "disabled": False,
            "private": False,
            "fork": True,  # Fork repository
            "license": "BSD 3-Clause License",
            "default_branch": "main",
            "size": 890,
            "last_update_api": datetime(2024, 5, 28, 14, 20, 0, tzinfo=timezone.utc),
            "created_at_api": datetime(2024, 1, 15, 9, 30, 0, tzinfo=timezone.utc),
            "last_update_str": "2 weeks ago",
            "avg_issue_resolution_time": None
        },
        {
            "name": "no-description-repo",
            "full_name": "fabriziosalmi/no-description-repo",
            "description": "",  # No description
            "url": "https://github.com/fabriziosalmi/no-description-repo",
            "stars": 3,
            "forks": 1,
            "watchers": 2,
            "commit_count": 8,
            "contributors_count": 1,
            "closed_issues_count": 0,
            "open_issues_count": 0,
            "language": "TypeScript",
            "archived": False,
            "disabled": False,
            "private": False,
            "fork": False,
            "license": "MIT License",
            "default_branch": "main",
            "size": 450,
            "last_update_api": datetime(2023, 12, 5, 11, 15, 0, tzinfo=timezone.utc),
            "created_at_api": datetime(2023, 10, 1, 13, 45, 0, tzinfo=timezone.utc),
            "last_update_str": "6 months ago",
            "avg_issue_resolution_time": 0.0
        }
    ]

def demonstrate_status_indicators(sample_data):
    """Demonstrate the enhanced status indicator functionality."""
    print("🎯 Status Indicator Demonstration")
    print("=" * 50)
    
    for repo in sample_data:
        status = get_repository_status_indicator(repo)
        repo_name = repo['name']
        
        # Remove Rich markup for clean display
        clean_status = status.replace('[yellow]', '').replace('[/yellow]', '') \
                           .replace('[red]', '').replace('[/red]', '') \
                           .replace('[dim]', '').replace('[/dim]', '') \
                           .replace('[cyan]', '').replace('[/cyan]', '')
        
        print(f"  {repo_name:25} -> {clean_status}")
    print()

def demonstrate_time_formatting():
    """Demonstrate time formatting improvements."""
    print("⏰ Time Formatting Demonstration")
    print("=" * 50)
    
    time_examples = [
        (3600, "1 hour"),
        (86400, "1 day"), 
        (604800, "1 week"),
        (1151978.5, "~13.3 days (avg issue resolution)"),
        (573356.0, "~6.6 days (avg issue resolution)"),
        (0.0, "No closed issues")
    ]
    
    for seconds, description in time_examples:
        formatted = format_resolution_time(seconds)
        print(f"  {description:35} -> {formatted}")
    print()

def demonstrate_insights(sample_data):
    """Demonstrate the repository insights functionality."""
    print("📊 Repository Insights Demonstration")
    print("=" * 50)
    
    insights = generate_repository_insights(sample_data)
    
    print(f"📈 Overview:")
    print(f"  Total repositories: {insights['total_repositories']}")
    print(f"  Archived repositories: {insights['archived_count']}")
    print(f"  Fork repositories: {insights['fork_count']}")
    print(f"  Total watchers: {insights['total_watchers']:,}")
    print(f"  Total open issues: {insights['total_open_issues']:,}")
    
    print(f"\n🔤 Language Distribution:")
    for language, count in insights['top_languages']:
        percentage = (count / insights['total_repositories']) * 100
        print(f"  {language:15} -> {count} repos ({percentage:.1f}%)")
    
    print(f"\n📅 Activity Distribution:")
    activity = insights['activity_distribution']
    print(f"  Active (≤30 days):   {activity['active']} repos")
    print(f"  Stale (30-180 days): {activity['stale']} repos") 
    print(f"  Inactive (>180 days): {activity['inactive']} repos")
    
    print(f"\n📦 Size Distribution:")
    size = insights['size_distribution']
    print(f"  Small (<1MB):   {size['small']} repos")
    print(f"  Medium (1-10MB): {size['medium']} repos")
    print(f"  Large (>10MB):   {size['large']} repos")
    
    print(f"\n🎂 Repository Ages:")
    ages = insights['repository_ages']
    print(f"  New (<1 year):     {ages['new']} repos")
    print(f"  Mature (1-5 years): {ages['mature']} repos")
    print(f"  Old (>5 years):     {ages['old']} repos")
    print()

def demonstrate_safe_file_operations():
    """Demonstrate safe file writing with backup/restore."""
    print("💾 Safe File Operations Demonstration") 
    print("=" * 50)
    
    demo_file = "demo_output.json"
    sample_content = {
        "demo": "Enhanced GitHub Stats",
        "features": [
            "Comprehensive error handling",
            "Enhanced repository metadata",
            "Visual status indicators", 
            "API rate limit optimization",
            "Statistical insights"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    def write_demo_content():
        with open(demo_file, 'w') as f:
            json.dump(sample_content, f, indent=2)
    
    print(f"  Writing demonstration data to {demo_file}...")
    success = safe_file_write(demo_file, write_demo_content)
    
    if success:
        print(f"  ✅ File written successfully with backup protection")
        
        # Verify content
        try:
            with open(demo_file, 'r') as f:
                data = json.load(f)
            print(f"  ✅ Content verified: {len(data['features'])} features listed")
        except Exception as e:
            print(f"  ❌ Content verification failed: {e}")
        
        # Clean up
        if os.path.exists(demo_file):
            os.remove(demo_file)
            print(f"  🧹 Cleaned up demo file")
    else:
        print(f"  ❌ File write failed")
    print()

def main():
    """Main demonstration function."""
    print("🚀 GitHub Repository Stats - Enhanced Features Demo")
    print("=" * 60)
    print("This demonstration shows the new features without using GitHub API calls.")
    print("=" * 60)
    print()
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Demonstrate all enhanced features
    demonstrate_status_indicators(sample_data)
    demonstrate_time_formatting()
    demonstrate_insights(sample_data)
    demonstrate_safe_file_operations()
    
    print("🎉 Feature Demonstration Complete!")
    print("=" * 60)
    print("Key Improvements Demonstrated:")
    print("✅ Enhanced status indicators (ARCHIVED, FORK, NO DESC, etc.)")
    print("✅ Improved time formatting with multiple units")
    print("✅ Comprehensive repository insights and statistics")
    print("✅ Safe file operations with backup/restore")
    print("✅ Rich metadata collection and analysis")
    print()
    print("🔧 Next Steps:")
    print("- Set up GitHub Personal Access Token (MY_PAT) for full functionality")
    print("- Run 'python stats.py' to generate live repository statistics")
    print("- Check SETUP.md for detailed configuration instructions")
    print("- Run 'python test_stats.py' to validate all functionality")

if __name__ == "__main__":
    main()
