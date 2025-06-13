# GitHub Repository Stats Setup Guide

## 🔧 Prerequisites

### GitHub Personal Access Token (PAT)
To avoid rate limiting and enable full functionality, you need a GitHub Personal Access Token:

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Set an expiration date and select the following scopes:
   - `public_repo` - Access public repositories
   - `read:user` - Read user profile data
   - `repo` - Full access to repositories (if you want private repo stats)

4. Copy the generated token

### Environment Setup

#### For Local Testing:
```bash
# Set the GitHub token as an environment variable
export MY_PAT="your_github_token_here"

# Or create a .env file (not tracked by git)
echo "MY_PAT=your_github_token_here" > .env
```

#### For GitHub Actions:
1. Go to your repository Settings > Secrets and variables > Actions
2. Add a new repository secret named `PAT` with your GitHub token as the value

## 🚀 Installation & Usage

### Local Installation
```bash
# Clone the repository
git clone https://github.com/your-username/repos.git
cd repos

# Install dependencies
pip install -r requirements.txt

# Run the stats generator
python stats.py
```

### Requirements
Make sure you have the following Python packages installed:
```
requests>=2.28.0
rich>=12.0.0
python-dateutil>=2.8.0
```

## 📊 Features Overview

### Data Collection
- Repository metadata (stars, forks, language, size, etc.)
- Commit count and contributor statistics
- Issue resolution times and counts
- Language distribution analysis
- Activity status determination

### Output Formats
- **Rich console table**: Interactive terminal display
- **Markdown table**: For README integration
- **HTML report**: Comprehensive web-based dashboard
- **Statistics insights**: Language and activity analysis

### Status Indicators
- 🏛️ **ARCHIVED**: Repository is archived
- ⚠️ **DISABLED**: Repository is disabled
- 🍴 **FORK**: Repository is a fork
- 😴 **INACTIVE**: No activity > 6 months
- 📅 **STALE**: No activity > 3 months
- ✅ **ACTIVE**: Recent activity
- 📝 **NO DESC**: Missing description
- 🔒 **PRIVATE**: Private repository

### Error Handling
- Comprehensive retry logic with exponential backoff
- Rate limit detection and automatic delays
- Backup/restore functionality for safe file operations
- Detailed logging for troubleshooting

## 🔍 Testing & Validation

### Test Rate Limiting
```bash
# Test with low rate limits (unauthenticated)
unset MY_PAT
python stats.py

# Test with authentication
export MY_PAT="your_token"
python stats.py
```

### Validate Outputs
```bash
# Check generated files
ls -la stats.md docs/index.html

# Validate markdown syntax
cat stats.md | head -20

# Check HTML structure
grep -E "<title>|<h1>" docs/index.html
```

### Monitor Logs
```bash
# Check log file for errors
tail -f github_stats.log

# Test specific functions
python -c "
from stats import validate_data_completeness
# Test data validation
print('Testing validation...')
"
```

## 🐛 Troubleshooting

### Common Issues

#### Rate Limit Errors
- **Symptom**: HTTP 403 errors with rate limit messages
- **Solution**: Set up GitHub PAT or wait for rate limit reset
- **Prevention**: Use `MY_PAT` environment variable

#### Authentication Errors
- **Symptom**: HTTP 401 errors
- **Solution**: Check PAT validity and permissions
- **Fix**: Regenerate token with correct scopes

#### Missing Data
- **Symptom**: Empty or incomplete repository data
- **Solution**: Check API responses and error logs
- **Debug**: Enable verbose logging

#### File Write Errors
- **Symptom**: Permission errors when writing output files
- **Solution**: Check file permissions and disk space
- **Recovery**: Use safe file write with backup/restore

## 📈 Performance Tips

1. **Use GitHub PAT**: Increases rate limit from 60 to 5,000 requests/hour
2. **Enable caching**: Reduces redundant API calls
3. **Filter repositories**: Focus on active repositories for faster processing
4. **Batch processing**: Process repositories in smaller batches for large accounts

## 🔧 Configuration Options

### Environment Variables
- `MY_PAT`: GitHub Personal Access Token
- `GITHUB_USERNAME`: Override default username detection
- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `OUTPUT_DIR`: Custom output directory for generated files

### Script Parameters
- Run with specific username: `python stats.py username`
- Debug mode: Add verbose logging throughout execution
- Custom output paths: Modify file paths in script constants

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with clear description

## 🔒 Security Notes

- Never commit GitHub tokens to the repository
- Use environment variables or GitHub Secrets for tokens
- Regularly rotate your GitHub Personal Access Tokens
- Monitor token usage in GitHub settings

## 📊 Advanced Usage

### Custom Analysis
```python
from stats import get_user_repositories_stats, generate_repository_insights

# Get repository data
repos = get_user_repositories_stats("username", "token")

# Generate custom insights
insights = generate_repository_insights(repos)
print(f"Total languages: {len(insights['languages'])}")
```

### Automated Workflows
The GitHub Actions workflow automatically:
- Runs daily at midnight UTC
- Updates repository statistics
- Handles errors with automatic issue creation
- Validates output files before deployment

## 📞 Support

For issues and questions:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review the logs in `github_stats.log`
3. Open an issue with detailed error information
4. Include relevant log snippets and environment details
