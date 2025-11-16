#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Health Check
Verifies all components are working correctly
"""

import os
import json
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def check_json_valid(filepath: str, description: str) -> bool:
    """Check if JSON file is valid"""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        print(f"✅ {description} is valid JSON")
        return True
    except FileNotFoundError:
        print(f"❌ {description} not found: {filepath}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ {description} has invalid JSON: {e}")
        return False


def main():
    """Run health checks"""
    print("\n🏥 Dashboard Health Check\n")
    print("=" * 60)
    
    checks_passed = 0
    checks_total = 0
    
    # Check core files
    print("\n📁 Core Files:")
    files = [
        ("README.md", "README"),
        ("requirements.txt", "Python dependencies"),
        ("stats.py", "Stats generator"),
        ("generate_badges.py", "Badge generator"),
        ("update_readme_badges.py", "README updater"),
        ("dev_server.py", "Development server"),
        ("Makefile", "Make configuration"),
        (".env.example", "Environment template"),
    ]
    
    for filepath, desc in files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Check documentation
    print("\n📚 Documentation:")
    docs = [
        ("SETUP.md", "Setup guide"),
        ("FEATURES.md", "Features documentation"),
        ("TUTORIAL.md", "Tutorial"),
        ("UPGRADE_SUMMARY.md", "Upgrade summary"),
    ]
    
    for filepath, desc in docs:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Check dashboard files
    print("\n🎨 Dashboard Files:")
    dashboard_files = [
        ("docs/index.html", "Main dashboard HTML"),
        ("docs/config.json", "Dashboard configuration"),
        ("docs/repositories-data.json", "Repository data"),
    ]
    
    for filepath, desc in dashboard_files:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Check generated files
    print("\n📊 Generated Files:")
    generated = [
        ("docs/STATS.md", "Statistics markdown"),
        ("docs/stats-summary.json", "Statistics JSON"),
    ]
    
    for filepath, desc in generated:
        checks_total += 1
        if check_file_exists(filepath, desc):
            checks_passed += 1
    
    # Check JSON validity
    print("\n🔍 JSON Validation:")
    json_files = [
        ("docs/repositories-data.json", "Repository data"),
        ("docs/stats-summary.json", "Statistics summary"),
        ("docs/config.json", "Dashboard config"),
    ]
    
    for filepath, desc in json_files:
        checks_total += 1
        if check_json_valid(filepath, desc):
            checks_passed += 1
    
    # Check badges directory
    print("\n🏅 Badges:")
    badges_dir = "docs/badges"
    if os.path.exists(badges_dir):
        badge_files = list(Path(badges_dir).glob("*.svg"))
        print(f"✅ Found {len(badge_files)} badge files")
        checks_passed += 1
    else:
        print(f"❌ Badges directory not found: {badges_dir}")
    checks_total += 1
    
    # Final summary
    print("\n" + "=" * 60)
    percentage = (checks_passed / checks_total * 100) if checks_total > 0 else 0
    print(f"\n📊 Summary: {checks_passed}/{checks_total} checks passed ({percentage:.1f}%)\n")
    
    if checks_passed == checks_total:
        print("🎉 All checks passed! Dashboard is healthy!")
        return 0
    elif percentage >= 80:
        print("⚠️  Most checks passed, but some issues found.")
        return 0
    else:
        print("❌ Multiple issues found. Please review the output above.")
        return 1


if __name__ == '__main__':
    exit(main())
