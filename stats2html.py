import os
import datetime
import logging
from urllib.parse import quote as url_quote

def create_html_report(repositories, total_stars, top_repo_full_names, username, format_resolution_time):
    """Creates an HTML report with responsive design and interactive elements."""
    # Get the script directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logging.info(f"Script directory: {script_dir}")
    
    # Try to create docs directory with explicit handling
    docs_dir = os.path.join(script_dir, "docs")
    try:
        if not os.path.exists(docs_dir):
            logging.info(f"Creating docs directory at: {docs_dir}")
            os.makedirs(docs_dir, exist_ok=True)
            if not os.path.exists(docs_dir):
                logging.error(f"Failed to create docs directory at: {docs_dir}")
        else:
            logging.info(f"Docs directory already exists at: {docs_dir}")
    except Exception as e:
        logging.error(f"Error creating docs directory: {e}")
        # Fall back to using the script directory if docs directory creation fails
        logging.info("Falling back to using script directory for HTML file")
        docs_dir = script_dir
    
    # Set HTML file path - use docs/index.html or fallback to ./index.html in script directory
    html_path = os.path.join(docs_dir, "index.html")
    abs_html_path = os.path.abspath(html_path)
    logging.info(f"Will save HTML report to absolute path: {abs_html_path}")
    
    # HTML template with CSS and JavaScript
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Stats for {username}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css">
    <style>
        :root {{
            --primary-color: #0d6efd;
            --secondary-color: #6c757d;
            --success-color: #198754;
            --info-color: #0dcaf0;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-color: #f8f9fa;
            --dark-color: #212529;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding-top: 20px;
            background-color: #f8f9fa;
        }}
        .card {{
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s, box-shadow 0.3s;
            margin-bottom: 20px;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }}
        .card-header {{
            border-radius: 10px 10px 0 0 !important;
            font-weight: bold;
        }}
        .stats-card {{
            text-align: center;
            padding: 1.5rem;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        .stat-label {{
            font-size: 1rem;
            color: var(--secondary-color);
        }}
        .progress {{
            height: 8px;
            margin-bottom: 1rem;
            border-radius: 4px;
        }}
        .chart-container {{
            height: 400px;
            margin-bottom: 1.5rem;
        }}
        .badge {{
            margin-right: 5px;
        }}
        .container {{
            max-width: 1200px;
        }}
        .navbar {{
            background-color: #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,.08);
        }}
        .navbar-brand {{
            font-weight: bold;
        }}
        .header-section {{
            padding: 3rem 0;
            background: linear-gradient(135deg, #0d6efd 0%, #0098ff 100%);
            color: white;
            margin-bottom: 2rem;
            border-radius: 15px;
        }}
        .avatar {{
            width: 120px;
            height: 120px;
            border-radius: 60px;
            border: 4px solid white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 3rem;
            padding: 1.5rem 0;
            background-color: #ffffff;
            border-top: 1px solid rgba(0,0,0,.1);
        }}
        .table-responsive {{
            border-radius: 10px;
            overflow: hidden;
        }}
        #repo-table {{
            width: 100%;
        }}
        #repo-table th {{
            font-weight: bold;
            background-color: #f8f9fa;
        }}
        .description-cell {{
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .stars-cell, .forks-cell, .commits-cell, .contributors-cell, .issues-cell {{
            text-align: right;
        }}
        .sparkline {{
            width: 100px;
            height: 30px;
        }}
        .star-icon {{
            color: #ffc107;
        }}
        .fork-icon {{
            color: #0d6efd;
        }}
        .commit-icon {{
            color: #6f42c1;
        }}
        .contributor-icon {{
            color: #198754;
        }}
        .issue-icon {{
            color: #dc3545;
        }}
        .project-card {{
            height: 100%;
        }}
        .project-card .card-body {{
            display: flex;
            flex-direction: column;
        }}
        .project-card .card-footer {{
            margin-top: auto;
        }}
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        @media (max-width: 768px) {{
            .header-section {{
                padding: 2rem 0;
            }}
            .stat-value {{
                font-size: 1.5rem;
            }}
            .avatar {{
                width: 80px;
                height: 80px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="navbar navbar-expand-lg navbar-light bg-light rounded mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-github me-2"></i>GitHub Stats
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <a class="nav-link" href="#overview">Overview</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#repositories">Repositories</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#star-history">Star History</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="https://github.com/{username}" target="_blank">
                                <i class="bi bi-box-arrow-up-right me-1"></i>GitHub Profile
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="header-section text-center" id="overview">
            <img src="https://github.com/{username}.png" alt="{username}" class="avatar mb-3">
            <h1>{username}</h1>
            <p class="lead">GitHub Repository Statistics</p>
            <div class="mt-4">
                <a href="https://github.com/{username}" class="btn btn-light me-2" target="_blank">
                    <i class="bi bi-github"></i> View Profile
                </a>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card stats-card">
                    <div class="stat-value text-primary">
                        <i class="bi bi-star-fill star-icon me-2"></i>{total_stars:,}
                    </div>
                    <div class="stat-label">Total Stars</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stats-card">
                    <div class="stat-value text-success">
                        <i class="bi bi-hdd-stack me-2"></i>{len(repositories):,}
                    </div>
                    <div class="stat-label">Repositories</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card stats-card">
                    <div class="stat-value text-info">
                        <i class="bi bi-people-fill me-2"></i>
                        {sum(r.get('contributors_count', 0) or 0 for r in repositories):,}
                    </div>
                    <div class="stat-label">Total Contributors</div>
                </div>
            </div>
        </div>
        
        <div class="card mb-4" id="star-history">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-graph-up me-2"></i>Star History (Top Repositories)
            </div>
            <div class="card-body">
                <div class="chart-container">
    """
    
    # Add the star history chart if we have repos
    if top_repo_full_names:
        num_chart_repos = min(len(top_repo_full_names), 10)
        chart_repo_names = top_repo_full_names[:num_chart_repos]
        repo_list_param = ",".join(url_quote(name) for name in chart_repo_names)
        chart_url = f"https://api.star-history.com/svg?repos={repo_list_param}&type=Date&theme=light"
        html_content += f"""
                    <img src="{chart_url}" class="img-fluid" alt="Star History Chart">
                    <div class="text-center mt-2">
                        <small class="text-muted">Chart shows star growth over time for top {num_chart_repos} repositories</small>
                    </div>
        """
    else:
        html_content += """
                    <div class="alert alert-info">
                        No repositories found to generate star history chart.
                    </div>
        """
    
    html_content += """
                </div>
            </div>
        </div>
        
        <div class="card mb-4" id="repositories">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-hdd-stack me-2"></i>Repositories
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table id="repo-table" class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>Repository</th>
                                <th>Description</th>
                                <th><i class="bi bi-star-fill star-icon"></i> Stars</th>
                                <th><i class="bi bi-diagram-2 fork-icon"></i> Forks</th>
                                <th><i class="bi bi-git commit-icon"></i> Commits</th>
                                <th><i class="bi bi-people contributor-icon"></i> Contributors</th>
                                <th><i class="bi bi-check-circle issue-icon"></i> Closed Issues</th>
                                <th><i class="bi bi-clock"></i> Last Update</th>
                                <th><i class="bi bi-hourglass-split"></i> Avg Issue Res.</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Add repository rows
    for repo in repositories:
        repo_name = repo.get('name', 'N/A')
        repo_url = repo.get('url', '#')
        description = repo.get('description', '')
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        commits = repo.get('commit_count')
        commits_str = f"{commits:,}" if commits is not None else "N/A"
        contributors = repo.get('contributors_count')
        contributors_str = f"{contributors:,}" if contributors is not None else "N/A"
        closed_issues = repo.get('closed_issues_count')
        closed_issues_str = f"{closed_issues:,}" if closed_issues is not None else "N/A"
        last_update = repo.get('last_update_str', 'Unknown')
        resolution_time = format_resolution_time(repo.get('avg_issue_resolution_time'))
        
        # Calculate style classes for values
        stars_class = "text-warning fw-bold" if stars > 100 else ""
        forks_class = "text-primary fw-bold" if forks > 50 else ""
        
        html_content += f"""
                            <tr>
                                <td><a href="{repo_url}" target="_blank">{repo_name}</a></td>
                                <td class="description-cell" title="{description}">{description}</td>
                                <td class="stars-cell {stars_class}">{stars:,}</td>
                                <td class="forks-cell {forks_class}">{forks:,}</td>
                                <td class="commits-cell">{commits_str}</td>
                                <td class="contributors-cell">{contributors_str}</td>
                                <td class="issues-cell">{closed_issues_str}</td>
                                <td>{last_update}</td>
                                <td>{resolution_time}</td>
                            </tr>
        """
    
    html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="row">
    """
    
    # Add top repositories as cards
    top_repos = sorted(repositories, key=lambda r: r.get('stars', 0) or 0, reverse=True)[:6]
    for repo in top_repos:
        repo_name = repo.get('name', 'N/A')
        repo_url = repo.get('url', '#')
        description = repo.get('description', 'No description')
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        last_update = repo.get('last_update_str', 'Unknown')
        
        html_content += f"""
            <div class="col-md-4 mb-4">
                <div class="card project-card h-100">
                    <div class="card-header bg-light">
                        <h5 class="card-title mb-0">
                            <a href="{repo_url}" target="_blank">{repo_name}</a>
                        </h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">{description}</p>
                    </div>
                    <div class="card-footer bg-white">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge bg-warning text-dark">
                                    <i class="bi bi-star-fill"></i> {stars:,}
                                </span>
                                <span class="badge bg-primary">
                                    <i class="bi bi-diagram-2"></i> {forks:,}
                                </span>
                            </div>
                            <small class="text-muted">Updated {last_update}</small>
                        </div>
                    </div>
                </div>
            </div>
        """
    
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    html_content += f"""
        </div>
        
        <footer class="footer text-center">
            <div class="container">
                <p class="mb-0">
                    Generated on {current_date} with 
                    <a href="https://github.com/{username}/repos/blob/main/stats.py" target="_blank">GitHub Stats Generator</a>
                </p>
            </div>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>
    <script>
        // Initialize DataTables
        $(document).ready(function() {{
            $('#repo-table').DataTable({{
                "order": [[2, "desc"]], // Sort by stars by default
                "pageLength": 25,
                "responsive": true,
                "language": {{
                    "search": "Filter repositories:",
                    "info": "Showing _START_ to _END_ of _TOTAL_ repositories",
                    "paginate": {{
                        "first": "<i class='bi bi-chevron-double-left'></i>",
                        "last": "<i class='bi bi-chevron-double-right'></i>",
                        "next": "<i class='bi bi-chevron-right'></i>",
                        "previous": "<i class='bi bi-chevron-left'></i>"
                    }}
                }}
            }});
            
            // Initialize tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {{
                return new bootstrap.Tooltip(tooltipTriggerEl);
            }});
        }});
    </script>
</body>
</html>
    """
    
    try:
        # Create parent directory if it doesn't exist (double-check)
        parent_dir = os.path.dirname(html_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            logging.info(f"Created parent directory: {parent_dir}")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            bytes_written = f.write(html_content)
            logging.info(f"HTML report successfully saved to: {abs_html_path} ({bytes_written} bytes written)")
        
        # Verify file was created
        if os.path.exists(html_path):
            file_size = os.path.getsize(html_path)
            logging.info(f"Verified file exists: {html_path} (Size: {file_size} bytes)")
            print(f"HTML report saved to: {abs_html_path}")
            
            # For GitHub Actions: Try to list directory contents for debugging
            try:
                logging.info(f"Contents of directory {os.path.dirname(html_path)}:")
                for f in os.listdir(os.path.dirname(html_path)):
                    logging.info(f"  - {f}")
            except Exception as e:
                logging.warning(f"Could not list directory contents: {e}")
            
            return True
        else:
            logging.error(f"File was not created at: {html_path}")
            print(f"Error: File was not created at: {html_path}")
            return False
    except IOError as e:
        logging.error(f"Error writing HTML file to {abs_html_path}: {e}")
        print(f"Error creating HTML report at {abs_html_path}: {e}")
        
        # Try alternate location as last resort
        try:
            alternate_path = os.path.join(script_dir, f"{username}_github_stats.html")
            logging.info(f"Trying alternate location: {alternate_path}")
            with open(alternate_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"HTML report saved to alternate location: {alternate_path}")
            print(f"HTML report saved to alternate location: {alternate_path}")
            return True
        except Exception as alt_e:
            logging.error(f"Error saving to alternate location: {alt_e}")
            return False
            
    except Exception as e:
        logging.error(f"Unexpected error writing HTML file: {e}")
        print(f"Unexpected error creating HTML report: {e}")
        return False
