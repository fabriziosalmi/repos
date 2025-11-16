# 🎬 Quick Start Tutorial

## 📚 Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running Locally](#running-locally)
4. [Deployment](#deployment)
5. [Customization](#customization)

---

## 1. Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/fabriziosalmi/repos.git
cd repos
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

**Expected output:**
```
✅ Successfully installed requests rich pytest...
```

---

## 2. Configuration

### Step 1: Create GitHub Personal Access Token

1. Go to **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token**
3. Give it a name (e.g., "Repos Dashboard")
4. Select scope: `public_repo` (or `repo` for private repositories)
5. Click **Generate token**
6. **Copy the token** (you won't see it again!)

### Step 2: Configure Environment Variables

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` and add your token:
```bash
MY_PAT=ghp_your_actual_token_here
```

**⚠️ Important:** Never commit `.env` to git!

---

## 3. Running Locally

### Option A: Using Make (Recommended)

```bash
# Fetch latest data
make stats

# Generate badges and statistics
make badges

# Start development server
make serve
```

Then open: **http://localhost:8000**

### Option B: Manual Commands

```bash
# 1. Fetch repository data
python stats.py

# 2. Generate badges
python generate_badges.py

# 3. Update README badges
python update_readme_badges.py

# 4. Start server
python dev_server.py
```

**Expected output:**
```
🚀 GitHub Repository Analytics Dashboard - Dev Server
================================================================

📂 Serving directory: /path/to/repos/docs
🌐 Server running at: http://localhost:8000
📊 Dashboard URL: http://localhost:8000/index.html

💡 Tips:
   • Press Ctrl+C to stop the server
   • Edit files and refresh browser to see changes
   • Run 'python stats.py' to update data
   • Run 'python generate_badges.py' to update badges

================================================================
```

### What You'll See

```
┌─────────────────────────────────────────────────────────┐
│  📊 GitHub Analytics Dashboard                         │
│                                           [Search...🔍] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ 88       │ │ 3,347    │ │ 230      │ │ 12       │ │
│  │ Repos    │ │ Stars    │ │ Forks    │ │ Languages│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                         │
│  [Sort: Stars ▼] [Language: All ▼] [Show Archived]    │
│                                                         │
│  📊 Charts Section                                      │
│  ┌──────────────┐ ┌──────────────┐                    │
│  │ Languages    │ │ Top Repos    │                    │
│  │  [Donut]     │ │  [Bar Chart] │                    │
│  └──────────────┘ └──────────────┘                    │
│                                                         │
│  📦 Repositories                                        │
│  ┌──────────────────────────────────────────┐          │
│  │ certmate                        ⭐ 898   │          │
│  │ SSL Certificate Management System        │          │
│  │ 🍴 53 forks  ❗ 2 issues  💾 120 commits│          │
│  │ [Python] Updated 2 weeks ago             │          │
│  └──────────────────────────────────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Deployment

### GitHub Pages (Automatic)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial dashboard setup"
   git push origin main
   ```

2. **Configure GitHub Pages**
   - Go to repository **Settings** → **Pages**
   - Source: **GitHub Actions**
   - Wait for workflow to complete (~2 minutes)

3. **Add GitHub Token Secret**
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `MY_PAT`
   - Value: Your GitHub token
   - Click **Add secret**

4. **Trigger Deployment**
   - Go to **Actions** tab
   - Click **Build and Deploy Dashboard**
   - Click **Run workflow**
   - Wait for completion
   - Visit: `https://YOUR_USERNAME.github.io/repos/`

### Manual Deployment

If you prefer manual control:

```bash
# Update all data
make update

# Commit changes
git add .
git commit -m "Update dashboard data"
git push origin main
```

GitHub Actions will automatically deploy!

---

## 5. Customization

### Change Colors

Edit `docs/index.html`, find the `:root` section:

```css
:root {
    --bg-primary: #0d1117;      /* Main background */
    --bg-secondary: #161b22;    /* Card background */
    --accent-blue: #58a6ff;     /* Links and highlights */
    --accent-green: #3fb950;    /* Success indicators */
    --accent-purple: #bc8cff;   /* Charts */
}
```

### Modify Charts

In `docs/index.html`, find chart rendering functions:

```javascript
function renderLanguageChart() {
    // Change chart type
    type: 'doughnut',  // Try: 'pie', 'bar', 'polarArea'
    
    // Change colors
    backgroundColor: ['#f1e05a', '#3572A5', ...],
    
    // Limit items shown
    .slice(0, 8)  // Show top 8
}
```

### Add Custom Metrics

Edit `generate_badges.py` to add new statistics:

```python
# Add new calculation
custom_metric = calculate_something(repositories)

# Add to badges list
badges.append(('custom', 'Custom', str(custom_metric), 'blue'))

# Add to markdown output
md_content += f"| Custom Metric | {custom_metric} |\n"
```

### Change Update Frequency

Edit `.github/workflows/deploy.yml`:

```yaml
schedule:
    - cron: '0 1 * * *'  # Daily at 1 AM UTC
    # Change to:
    - cron: '0 */6 * * *'  # Every 6 hours
    # or
    - cron: '0 0 * * 0'  # Weekly on Sunday
```

---

## 🎯 Common Tasks

### Update Data
```bash
make update
```

### Clean Cache
```bash
make clean
```

### Run Tests
```bash
make test
```

### View Logs
```bash
tail -f github_stats.log
```

### Check Generated Files
```bash
ls -lh docs/badges/
cat docs/STATS.md
cat docs/stats-summary.json
```

---

## 🐛 Troubleshooting

### Problem: "Rate limit exceeded"
**Solution:** Wait 1 hour or use a GitHub token with higher limits

### Problem: "No data displayed"
**Solution:** Check `docs/repositories-data.json` exists and is valid JSON

### Problem: "Charts not rendering"
**Solution:** Open browser console (F12) and check for JavaScript errors

### Problem: "GitHub Actions failing"
**Solution:** 
1. Check if `MY_PAT` secret is set
2. Verify token has correct permissions
3. Check Actions log for specific errors

---

## 📚 Next Steps

- ✅ Customize the theme colors
- ✅ Add more repositories to analyze
- ✅ Share your dashboard URL
- ✅ Star the repository if you find it useful!
- ✅ Contribute improvements via pull requests

---

## 🙋 Need Help?

- 📖 [Read the full documentation](SETUP.md)
- ✨ [Browse all features](FEATURES.md)
- 🐛 [Report issues](https://github.com/fabriziosalmi/repos/issues)
- 💬 [Ask questions](https://github.com/fabriziosalmi/repos/discussions)

---

**Happy Analyzing! 🎉**
