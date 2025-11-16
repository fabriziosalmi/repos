# 🚀 Quick Reference Guide

## 📝 Common Commands

### Setup & Installation
```bash
# Clone repository
git clone https://github.com/fabriziosalmi/repos.git
cd repos

# Install dependencies
make install
# or
pip install -r requirements.txt

# Configure token
cp .env.example .env
# Edit .env and add your GitHub token
```

### Development
```bash
# Update all data
make update

# Start dev server (http://localhost:8000)
make serve

# Generate badges only
make badges

# Fetch stats only  
make stats

# Clean generated files
make clean

# Run tests
make test

# Health check
python health_check.py
```

### Individual Scripts
```bash
# Fetch GitHub repository data
python stats.py

# Generate badges and statistics
python generate_badges.py

# Update README badges
python update_readme_badges.py

# Start development server
python dev_server.py
```

### Deployment
```bash
# Prepare for deployment
make deploy

# Push to GitHub
git add .
git commit -m "Update dashboard"
git push origin main

# GitHub Actions will auto-deploy to Pages
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `docs/index.html` | Main dashboard UI |
| `docs/repositories-data.json` | Repository data |
| `docs/STATS.md` | Detailed statistics |
| `docs/stats-summary.json` | JSON API |
| `docs/badges/*.svg` | Custom badges |
| `README.md` | Main documentation |
| `FEATURES.md` | Feature list |
| `TUTORIAL.md` | Step-by-step guide |

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
MY_PAT=your_github_token          # Required
GITHUB_USERNAME=your_username     # Optional
CACHE_DURATION_HOURS=1            # Optional
PORT=8000                         # Optional
VERBOSE=true                      # Optional
```

### Dashboard Config (docs/config.json)
```json
{
  "dashboard": {
    "title": "Your Title",
    "description": "Your Description"
  },
  "theme": {
    "primary": "#58a6ff"
  }
}
```

---

## 🎨 Customization

### Change Colors (docs/index.html)
```css
:root {
    --bg-primary: #0d1117;
    --accent-blue: #58a6ff;
}
```

### Modify Charts (docs/index.html)
```javascript
function renderLanguageChart() {
    // Change type: 'doughnut', 'pie', 'bar', etc.
    // Change colors
    // Adjust data limits
}
```

### Add Custom Badges (generate_badges.py)
```python
badges.append(('filename', 'Label', 'Value', 'color'))
```

---

## 🐛 Troubleshooting

### Problem: Rate limit exceeded
```bash
# Wait 1 hour or use authenticated token
export MY_PAT="your_token"
python stats.py
```

### Problem: No data displayed
```bash
# Check if data file exists and is valid
ls -lh docs/repositories-data.json
python -m json.tool docs/repositories-data.json
```

### Problem: Charts not rendering
```bash
# Check browser console (F12)
# Verify Chart.js is loading
# Check for JavaScript errors
```

### Problem: Port already in use
```bash
# Use different port
PORT=3000 python dev_server.py
```

---

## 📊 GitHub Actions

### Workflow Triggers
- **Push to main**: Automatic deployment
- **Daily schedule**: 1:00 AM UTC
- **Manual**: Actions tab → Run workflow

### Required Secrets
- `MY_PAT`: GitHub Personal Access Token

### Workflow Steps
1. Fetch repository data
2. Generate badges
3. Update README
4. Deploy to Pages

---

## 🔗 Useful URLs

### Local Development
- Dashboard: http://localhost:8000
- Stats: http://localhost:8000/STATS.md
- Config: http://localhost:8000/config.json

### Production
- Live Dashboard: https://USERNAME.github.io/repos/
- Repository: https://github.com/USERNAME/repos
- Actions: https://github.com/USERNAME/repos/actions

---

## 📖 Documentation Links

- [Main README](README.md)
- [Quick Start Tutorial](TUTORIAL.md)
- [Setup Guide](SETUP.md)
- [Features List](FEATURES.md)
- [Upgrade Summary](UPGRADE_SUMMARY.md)

---

## 💡 Pro Tips

1. **Auto-update README**: Run `make update` before committing
2. **Test locally**: Always run `make serve` to test changes
3. **Check health**: Run `python health_check.py` regularly
4. **Clean cache**: Use `make clean` if data seems stale
5. **Watch logs**: Check GitHub Actions logs for deployment issues

---

## 🎯 Workflow Examples

### Morning Update Routine
```bash
make update          # Fetch latest data
make serve           # Preview locally
# Review changes in browser
git add .
git commit -m "Daily update"
git push
```

### Adding New Features
```bash
# Edit docs/index.html
make serve           # Test changes
# Verify in browser
git add docs/index.html
git commit -m "Add new feature"
git push
```

### Debugging Issues
```bash
make clean           # Clear cache
python stats.py      # Re-fetch data
python health_check.py  # Verify setup
make serve           # Test locally
```

---

**Quick help**: Run `make help` for all available commands
