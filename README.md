# My GitHub Repositories Dashboard

This project presents an interactive dashboard showcasing my GitHub repositories. It automatically fetches data using a Python script and displays it in a modern, searchable, and sortable web interface built with Vue.js and Vite.

The entire process, from data generation to deployment, is automated via GitHub Actions.

**[➡️ View the Live Dashboard](https://fabriziosalmi.github.io/repos/)**



---

## ✨ Features

The dashboard provides a comprehensive and interactive overview of my repositories:

-   **🚀 Modern UI**: A clean, "cyberpunk" themed interface built with Vue 3, Vite, and Tailwind CSS.
-   **⚡ Real-time Search**: Instantly filter repositories by name.
-   **🔄 Dynamic Sorting**: Sort repositories by the number of stars or by the last update time.
-   **📊 Language Distribution**: A donut chart visualizes the programming languages used across all my projects.
-   **🤖 Automated Data**: A Python script fetches the latest data from the GitHub API.
-   **CI/CD Pipeline**: A GitHub Actions workflow automatically regenerates the data, builds the frontend, and deploys it to GitHub Pages.

## 🛠️ Development

To run the project locally, you need to set up both the Python data generator and the frontend application.

### 1. Data Generation (Python)

The Python script `stats.py` is responsible for fetching data from the GitHub API and saving it as a JSON file.

1.  **Set up a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up GitHub Token:**
    To avoid rate limiting, the script requires a GitHub Personal Access Token (PAT). Create a token with the `public_repo` scope.
    
    Export the token as an environment variable:
    ```bash
    export MY_PAT="your_github_token_here"
    ```

4.  **Run the script:**
    ```bash
    python stats.py
    ```
    This will create a `public_data/repositories-data.json` file.

### 2. Frontend (Vite + Vue)

The frontend is a Vite-powered Vue 3 application.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Copy the data file:**
    The development server needs the data file to be in the `frontend/public` directory.
    ```bash
    cp ../public_data/repositories-data.json public/
    ```

4.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## 🚀 Deployment

Deployment is handled automatically by the `.github/workflows/deploy.yml` GitHub Actions workflow. The workflow is triggered on:
-   A `push` to the `main` branch.
-   A daily schedule (`cron`).
-   Manual dispatch via the Actions tab.

The workflow consists of two main jobs:
1.  **`build-data`**: Runs the `stats.py` script to generate the `repositories-data.json` file and uploads it as an artifact.
2.  **`build-and-deploy`**: Downloads the data artifact, builds the Vite application, and deploys the result to GitHub Pages.