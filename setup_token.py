#!/usr/bin/env python3
"""
GitHub Token Setup Helper
Assists with setting up GitHub Personal Access Token for enhanced functionality.
"""

import os
import sys
import subprocess
import requests
from getpass import getpass

def check_current_token():
    """Check if a GitHub token is currently configured."""
    token = os.environ.get('MY_PAT')
    if token:
        print(f"✅ GitHub token found in MY_PAT environment variable")
        
        # Test the token
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                core_limit = data.get("resources", {}).get("core", {})
                remaining = core_limit.get("remaining", 0)
                limit = core_limit.get("limit", 0)
                reset_time = core_limit.get("reset", 0)
                
                print(f"✅ Token is valid")
                print(f"📊 Rate limit: {remaining}/{limit} remaining")
                
                if remaining < 100:
                    from datetime import datetime
                    reset_datetime = datetime.fromtimestamp(reset_time)
                    print(f"⚠️  Rate limit is low. Resets at: {reset_datetime}")
                
                return True
            else:
                print(f"❌ Token validation failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error validating token: {e}")
            return False
    else:
        print("❌ No GitHub token found in MY_PAT environment variable")
        return False

def get_token_instructions():
    """Provide instructions for creating a GitHub Personal Access Token."""
    print("\n🔧 GitHub Personal Access Token Setup Instructions")
    print("=" * 60)
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Set a descriptive name (e.g., 'Repository Stats')")
    print("4. Set expiration (recommend 90 days or custom)")
    print("5. Select these scopes:")
    print("   ☑️  public_repo - Access public repositories")
    print("   ☑️  read:user - Read user profile data")
    print("   ☑️  repo (optional) - Full access for private repos")
    print("6. Click 'Generate token'")
    print("7. Copy the generated token (starts with 'ghp_' or 'github_pat_')")
    print()

def set_token_temporarily():
    """Set the token for the current session."""
    print("🔐 Set GitHub Token for Current Session")
    print("=" * 50)
    
    token = getpass("Enter your GitHub Personal Access Token: ")
    
    if not token or len(token) < 10:
        print("❌ Invalid token provided")
        return False
    
    # Set environment variable for current session
    os.environ['MY_PAT'] = token
    
    # Test the token
    try:
        headers = {"Authorization": f"token {token}"}
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            username = user_data.get('login', 'unknown')
            print(f"✅ Token validated successfully!")
            print(f"👤 Authenticated as: {username}")
            print(f"🎯 Token set for current session only")
            print(f"💡 To make permanent, add to your shell profile:")
            print(f"   export MY_PAT=\"{token[:12]}...\"")
            return True
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error validating token: {e}")
        return False

def run_stats_with_token():
    """Run the stats script with the configured token."""
    print("\n🚀 Running Repository Stats...")
    print("=" * 40)
    
    try:
        # Run the stats script
        result = subprocess.run([sys.executable, "stats.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Stats generation completed successfully!")
            print("📊 Check the generated files:")
            print("   - fabriziosalmi_github_stats.md")
            print("   - docs/index.html")
            print("   - fabriziosalmi_github_stats.json")
        else:
            print("❌ Stats generation failed:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⚠️  Stats generation timed out (>5 minutes)")
    except Exception as e:
        print(f"❌ Error running stats: {e}")

def create_env_file():
    """Create a .env file for token storage."""
    print("\n💾 Create .env File for Token Storage")
    print("=" * 50)
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Overwrite existing .env file? (y/N): ")
        if response.lower() != 'y':
            return False
    
    token = getpass("Enter your GitHub Personal Access Token: ")
    
    if not token or len(token) < 10:
        print("❌ Invalid token provided")
        return False
    
    try:
        with open('.env', 'w') as f:
            f.write(f"MY_PAT={token}\n")
            f.write("# GitHub Personal Access Token for repository stats\n")
        
        print("✅ .env file created successfully!")
        print("💡 Load with: source .env (or use python-dotenv)")
        print("⚠️  Important: .env file is in .gitignore (not tracked)")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    """Main setup helper function."""
    print("🔧 GitHub Repository Stats - Token Setup Helper")
    print("=" * 60)
    
    # Check current status
    token_configured = check_current_token()
    
    if token_configured:
        print("\n🎉 GitHub token is properly configured!")
        response = input("\nRun repository stats now? (Y/n): ")
        if response.lower() != 'n':
            run_stats_with_token()
        return
    
    print("\n🚀 GitHub token setup required for full functionality")
    print("\nOptions:")
    print("1. View setup instructions")
    print("2. Set token for current session")
    print("3. Create .env file for token storage")
    print("4. Test without token (limited functionality)")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                get_token_instructions()
            elif choice == '2':
                if set_token_temporarily():
                    response = input("\nRun repository stats now? (Y/n): ")
                    if response.lower() != 'n':
                        run_stats_with_token()
                    break
            elif choice == '3':
                if create_env_file():
                    print("💡 Restart terminal or run 'source .env' to load token")
                    break
            elif choice == '4':
                print("\n⚠️  Running without token (rate limited to 60 requests/hour)")
                response = input("Continue anyway? (y/N): ")
                if response.lower() == 'y':
                    run_stats_with_token()
                break
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
