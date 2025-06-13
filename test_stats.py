#!/usr/bin/env python3
"""
Test script for GitHub Repository Stats functionality.
Tests various features with minimal API calls to avoid rate limiting.
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
    validate_data_completeness,
    safe_file_write,
    generate_repository_insights
)

def test_status_indicators():
    """Test the status indicator functionality."""
    print("🧪 Testing Status Indicators...")
    
    test_cases = [
        {"archived": True, "disabled": False, "description": "Test repo", "expected": "ARCHIVED"},
        {"archived": False, "disabled": True, "description": "Test repo", "expected": "DISABLED"},
        {"archived": False, "disabled": False, "description": "", "expected": "NO DESC"},
        {"archived": False, "disabled": False, "description": "Test repo", "fork": True, "expected": "FORK"},
    ]
    
    for case in test_cases:
        result = get_repository_status_indicator(case)
        expected = case.get("expected", "UNKNOWN")
        # Check if the expected text is in the result (since result contains Rich markup)
        status = "✅ PASS" if expected in result else "❌ FAIL"
        print(f"  {status}: {case} -> {result} (expected: {expected})")

def test_time_formatting():
    """Test time duration formatting."""
    print("\n🕒 Testing Time Formatting...")
    
    test_cases = [
        (3600, "1h"),  # 1 hour
        (86400, "1d"),  # 1 day
        (90061, "1d 1h 1m 1s"),  # 1 day, 1 hour, 1 minute, 1 second
    ]
    
    for seconds, expected in test_cases:
        result = format_resolution_time(seconds)
        status = "✅ PASS" if expected in result else "❌ FAIL"
        print(f"  {status}: {seconds}s -> {result} (expected to contain: {expected})")

def test_data_validation():
    """Test data validation functionality."""
    print("\n📊 Testing Data Validation...")
    
    # Test with valid data (need to convert to list format as expected by function)
    valid_data = [
        {"name": "repo1", "full_name": "user/repo1", "stars": 10, "forks": 2, "description": "Test repo", "url": "https://github.com/user/repo1"},
        {"name": "repo2", "full_name": "user/repo2", "stars": 5, "forks": 1, "description": "Another repo", "url": "https://github.com/user/repo2"}
    ]
    
    is_valid, message = validate_data_completeness(valid_data, 15)
    status = "✅ PASS" if is_valid else "❌ FAIL"
    print(f"  {status}: Valid data validation - {message}")
    
    # Test with incomplete data
    invalid_data = [
        {"name": "repo1", "stars": None, "forks": 2, "description": "Test repo"},  # Missing required fields
        {"name": "repo2", "stars": 5, "forks": None, "description": ""}
    ]
    
    is_valid, message = validate_data_completeness(invalid_data, 5)
    status = "✅ PASS" if not is_valid else "❌ FAIL"
    print(f"  {status}: Invalid data validation - {message}")

def test_safe_file_write():
    """Test safe file writing functionality."""
    print("\n💾 Testing Safe File Write...")
    
    test_file = "test_output.txt"
    test_content = "Test content for safe file write"
    
    try:
        # Create a write function that writes to the test file
        def write_test_content():
            with open(test_file, 'w') as f:
                f.write(test_content)
        
        success = safe_file_write(test_file, write_test_content)
        
        if success and os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            
            if content == test_content:
                print("  ✅ PASS: Safe file write successful")
            else:
                print("  ❌ FAIL: Content mismatch")
        else:
            print("  ❌ FAIL: File write failed")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            
    except Exception as e:
        print(f"  ❌ FAIL: Exception during file write: {e}")

def test_insights_generation():
    """Test repository insights generation."""
    print("\n📈 Testing Insights Generation...")
    
    sample_repos = [
        {
            "language": "Python",
            "archived": False,
            "disabled": False,
            "last_update_api": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            "stars": 100,
            "watchers": 10,
            "open_issues_count": 5,
            "fork": False,
            "size": 500
        },
        {
            "language": "JavaScript", 
            "archived": True,
            "disabled": False,
            "last_update_api": datetime(2023, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            "stars": 50,
            "watchers": 3,
            "open_issues_count": 2,
            "fork": True,
            "size": 1500
        }
    ]
    
    try:
        insights = generate_repository_insights(sample_repos)
        
        if insights and "language_distribution" in insights and "activity_distribution" in insights:
            print("  ✅ PASS: Insights generation successful")
            print(f"    Languages found: {list(insights['language_distribution'].keys())}")
            print(f"    Activity distribution: {insights['activity_distribution']}")
            print(f"    Total repositories: {insights['total_repositories']}")
        else:
            print("  ❌ FAIL: Invalid insights structure")
            
    except Exception as e:
        print(f"  ❌ FAIL: Exception during insights generation: {e}")

def test_github_api_connection():
    """Test basic GitHub API connectivity without consuming many requests."""
    print("\n🌐 Testing GitHub API Connection...")
    
    token = os.environ.get('MY_PAT')
    
    if token:
        print("  ✅ GitHub token found in MY_PAT environment variable")
        headers = {"Authorization": f"token {token}"}
    else:
        print("  ⚠️  No GitHub token found - using unauthenticated requests")
        headers = {}
    
    try:
        import requests
        
        # Test with a simple API call that doesn't count against rate limits much
        response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        
        if response.status_code == 200:
            rate_limit_info = response.json()
            core_limit = rate_limit_info.get("resources", {}).get("core", {})
            remaining = core_limit.get("remaining", 0)
            limit = core_limit.get("limit", 0)
            
            print(f"  ✅ PASS: GitHub API accessible")
            print(f"    Rate limit: {remaining}/{limit} remaining")
            
            if remaining < 10:
                print("  ⚠️  WARNING: Very low rate limit remaining!")
                return False
            
            return True
        else:
            print(f"  ❌ FAIL: API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ FAIL: Exception during API test: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GitHub Repository Stats - Test Suite")
    print("=" * 50)
    
    # Run all tests
    test_status_indicators()
    test_time_formatting()
    test_data_validation()
    test_safe_file_write()
    test_insights_generation()
    api_ok = test_github_api_connection()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    if api_ok:
        print("✅ All basic functionality tests completed")
        print("✅ GitHub API is accessible")
        
        # Check if we can run a minimal version of the main script
        print("\n🏃 Running minimal stats collection test...")
        
        try:
            # Import and run a minimal test
            from stats import make_github_request
            
            token = os.environ.get('MY_PAT')
            headers = {"Authorization": f"token {token}"} if token else {}
            
            # Test with a simple user API call
            response = make_github_request("https://api.github.com/user", headers)
            
            if response and response.status_code == 200:
                user_data = response.json()
                print(f"✅ Successfully authenticated as: {user_data.get('login', 'unknown')}")
            else:
                print("⚠️  API call failed, but basic functionality is working")
                
        except Exception as e:
            print(f"⚠️  Minor issue with API test: {e}")
    else:
        print("⚠️  Some tests completed, but GitHub API access is limited")
    
    print("\n🔧 Setup Recommendations:")
    if not os.environ.get('MY_PAT'):
        print("- Set up GitHub Personal Access Token (MY_PAT environment variable)")
        print("- See SETUP.md for detailed instructions")
    
    print("- Run 'python stats.py' to generate full repository statistics")
    print("- Check github_stats.log for detailed execution logs")

if __name__ == "__main__":
    main()
