# fabriziosalmi.github.io/repos

Personal portfolio site — auto-updated from GitHub data.

[**→ Live site**](https://fabriziosalmi.github.io/repos/)

## What this repo does

1. A nightly GitHub Action (`deploy.yml`) calls the GitHub API and writes
   `public_data/repositories-data.json` (via [`stats.py`](stats.py)).
2. That JSON is fed to an Astro site in [`astro-frontend/`](astro-frontend/) which
   renders the portfolio in [`docs/`](docs/) for GitHub Pages.
3. A separate weekly job (`weekly-report.yml`) generates a report from the same
   data via [`reporter.py`](reporter.py) and commits it under [`reports/`](reports/).

That's the whole loop. The Python at the root is the data layer; the Astro
project is the presentation layer.

## Local development

```bash
# Data (needs a GitHub PAT)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export MY_PAT=ghp_...
python stats.py                  # writes public_data/repositories-data.json

# Site
cd astro-frontend
npm install
cp ../public_data/repositories-data.json src/data/repositories.json
npm run dev                      # http://localhost:4321/repos/
```

## Layout

| Path | Role |
|---|---|
| [`stats.py`](stats.py) | GitHub API client + cache + aggregations |
| [`aggregate_contributors.py`](aggregate_contributors.py) | Cross-repo contributor stats |
| [`reporter.py`](reporter.py) | Weekly report generator |
| [`threshold_monitor.py`](threshold_monitor.py) | Diff detector → Discord/Slack webhooks |
| [`generate_badges.py`](generate_badges.py) | SVG badge writer |
| [`astro-frontend/`](astro-frontend/) | Portfolio site (Astro + Tailwind) |
| [`docs/`](docs/) | Built site, served by GitHub Pages (force-pushed by CI) |
| [`reports/`](reports/) | Weekly markdown reports, committed by CI |

## Configuration

- `MY_PAT` — GitHub Personal Access Token (`public_repo` scope).
- `DISCORD_WEBHOOK_URL`, `SLACK_WEBHOOK_URL` — optional, for threshold alerts.
- `SENDGRID_API_KEY`, `REPORT_EMAIL` — optional, for emailed weekly reports.

## License

[MIT](LICENSE).
