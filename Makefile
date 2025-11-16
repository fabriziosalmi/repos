.PHONY: help install update serve badges stats clean test deploy

# Default target
help:
	@echo "🚀 GitHub Repository Analytics Dashboard - Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install Python dependencies"
	@echo "  make update     - Update repository data and badges"
	@echo "  make serve      - Start local development server"
	@echo "  make badges     - Generate badges and statistics"
	@echo "  make stats      - Fetch latest GitHub statistics"
	@echo "  make clean      - Clean generated files and cache"
	@echo "  make test       - Run tests"
	@echo "  make deploy     - Deploy to GitHub Pages (requires commit)"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Update everything
update: stats badges
	@echo "✅ All data updated successfully!"

# Start development server
serve:
	@echo "🌐 Starting development server..."
	python dev_server.py

# Generate badges and statistics
badges:
	@echo "📛 Generating badges and statistics..."
	python generate_badges.py
	python update_readme_badges.py
	@echo "✅ Badges generated!"

# Fetch latest statistics
stats:
	@echo "📊 Fetching latest GitHub statistics..."
	python stats.py
	@echo "✅ Statistics updated!"

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	rm -rf docs/badges/
	rm -f docs/STATS.md
	rm -f docs/stats-summary.json
	rm -f github_stats_cache.json
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleaned!"

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest -v
	@echo "✅ Tests passed!"

# Deploy (requires git commit)
deploy:
	@echo "🚀 Preparing deployment..."
	@make update
	@echo ""
	@echo "📝 Ready to deploy!"
	@echo "   Next steps:"
	@echo "   1. git add ."
	@echo "   2. git commit -m 'Update dashboard data'"
	@echo "   3. git push origin main"
	@echo ""
	@echo "   GitHub Actions will automatically deploy to GitHub Pages"
