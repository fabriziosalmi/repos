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
    
    # Calculate totals for additional metrics
    total_forks = sum(r.get('forks', 0) or 0 for r in repositories)
    total_commits = sum(r.get('commit_count', 0) or 0 for r in repositories)
    total_closed_issues = sum(r.get('closed_issues_count', 0) or 0 for r in repositories)
    
    # Calculate average issue resolution time across all repos
    valid_times = [r.get('avg_issue_resolution_time') for r in repositories if r.get('avg_issue_resolution_time')]
    avg_resolution_time = sum(valid_times) / len(valid_times) if valid_times else None
    avg_resolution_time_str = format_resolution_time(avg_resolution_time) if avg_resolution_time else "N/A"
    
    # HTML template with CSS and JavaScript
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Stats for {username}</title>
    <meta name="description" content="Detailed GitHub statistics and analysis for {username}">
    <link rel="icon" href="https://github.com/favicon.ico" type="image/x-icon">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
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
            
            /* Dark mode variables */
            --dark-bg: #121212;
            --dark-card-bg: #1e1e1e;
            --dark-text: #e0e0e0;
            --dark-secondary-text: #aaaaaa;
            --dark-border: #2d2d2d;
            --dark-hover: #2a2a2a;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding-top: 20px;
            background-color: var(--light-color);
            transition: background-color 0.3s ease;
        }}
        
        body.dark-mode {{
            background-color: var(--dark-bg);
            color: var(--dark-text);
        }}
        
        .container {{
            max-width: 1200px;
            animation: fadeIn 0.8s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .card {{
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            margin-bottom: 20px;
            overflow: hidden;
            border: none;
        }}
        
        .dark-mode .card {{
            background-color: var(--dark-card-bg);
            border-color: var(--dark-border);
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }}
        
        .card-header {{
            border-radius: 12px 12px 0 0 !important;
            font-weight: bold;
            border-bottom: none;
            padding: 0.8rem 1.25rem;
        }}
        
        .dark-mode .card-header {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: var(--dark-text);
        }}
        
        .dark-mode .card-header.bg-primary {{
            background-color: #0d6efd !important;
        }}
        
        .stats-card {{
            text-align: center;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        
        .stats-card:hover {{
            background-color: rgba(var(--primary-color-rgb), 0.05);
        }}
        
        .dark-mode .stats-card:hover {{
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        .stat-value {{
            font-size: 2.25rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }}
        
        .stats-card:hover .stat-value {{
            transform: scale(1.1);
        }}
        
        .stat-label {{
            font-size: 1rem;
            color: var(--secondary-color);
            transition: color 0.3s ease;
        }}
        
        .dark-mode .stat-label {{
            color: var(--dark-secondary-text);
        }}
        
        .progress {{
            height: 8px;
            margin-bottom: 1rem;
            border-radius: 4px;
        }}
        
        .chart-container {{
            height: 400px;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .chart-container .loading {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: rgba(255,255,255,0.7);
        }}
        
        .dark-mode .chart-container .loading {{
            background-color: rgba(0,0,0,0.5);
        }}
        
        .badge {{
            margin-right: 5px;
            padding: 0.5em 0.8em;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .badge:hover {{
            transform: scale(1.1);
        }}
        
        .navbar {{
            background-color: #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,.08);
            border-radius: 12px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }}
        
        .dark-mode .navbar {{
            background-color: var(--dark-card-bg);
        }}
        
        .navbar-brand {{
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        
        .dark-mode .navbar-brand, .dark-mode .nav-link {{
            color: var(--dark-text) !important;
        }}
        
        .dark-mode .navbar-toggler {{
            border-color: var(--dark-border);
        }}
        
        .header-section {{
            padding: 3rem 0;
            background: linear-gradient(135deg, #0d6efd 0%, #0098ff 100%);
            color: white;
            margin-bottom: 2rem;
            border-radius: 15px;
            position: relative;
            overflow: hidden;
        }}
        
        .header-section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><path fill="%23FFFFFF" fill-opacity="0.1" d="M37.5,186c-12.1-10.5-11.8-32.3-7.2-46.7c4.8-15,13.1-17.8,30.1-36.7C91,68.8,83.5,56.7,103.5,45.5c22.7-12.7,45.7,1,54.5,11.9c8.9,11,13.8,21,13.8,36.8c0,22.5-3.7,40.8-28.3,54.6c-22.6,12.7-33.5,10.1-44.7,25.7c-13.3,18.6-23.1,21.2-37.5,11.5z" /></svg>') no-repeat center center;
            background-size: 600px;
            opacity: 0.3;
            pointer-events: none;
            animation: rotate 60s linear infinite;
        }}
        
        @keyframes rotate {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .avatar {{
            width: 120px;
            height: 120px;
            border-radius: 60px;
            border: 4px solid white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
        }}
        
        .avatar:hover {{
            transform: scale(1.1);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        
        .footer {{
            margin-top: 3rem;
            padding: 1.5rem 0;
            background-color: #ffffff;
            border-top: 1px solid rgba(0,0,0,.1);
            border-radius: 12px;
            transition: all 0.3s ease;
        }}
        
        .dark-mode .footer {{
            background-color: var(--dark-card-bg);
            border-color: var(--dark-border);
            color: var(--dark-text);
        }}
        
        .table-responsive {{
            border-radius: 10px;
            overflow: hidden;
        }}
        
        #repo-table {{
            width: 100%;
        }}
        
        .dark-mode #repo-table {{
            color: var(--dark-text);
        }}
        
        #repo-table th {{
            font-weight: bold;
            background-color: #f8f9fa;
            border-bottom: none;
        }}
        
        .dark-mode #repo-table th {{
            background-color: rgba(255, 255, 255, 0.05);
            color: var(--dark-text);
        }}
        
        .dark-mode .table-striped>tbody>tr:nth-of-type(odd) {{
            background-color: rgba(255, 255, 255, 0.02);
        }}
        
        .dark-mode .table {{
            border-color: var(--dark-border);
        }}
        
        .description-cell {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            line-height: 1.3;
        }}
        
        .stars-cell, .forks-cell, .commits-cell, .contributors-cell, .issues-cell {{
            text-align: right;
            font-variant-numeric: tabular-nums;
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
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .project-card::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(to right, #0d6efd, #0098ff);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }}
        
        .project-card:hover::after {{
            transform: scaleX(1);
        }}
        
        .project-card .card-body {{
            display: flex;
            flex-direction: column;
        }}
        
        .project-card .card-footer {{
            margin-top: auto;
            border-top: none;
            background-color: transparent;
        }}
        
        .dark-mode .project-card .card-footer {{
            background-color: transparent;
        }}
        
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 5px;
            margin-bottom: 5px;
            transition: all 0.2s ease;
        }}
        
        .tag:hover {{
            transform: scale(1.05);
        }}
        
        .theme-switch {{
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }}
        
        .theme-switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        
        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }}
        
        .slider:before {{
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}
        
        input:checked + .slider {{
            background-color: #2196F3;
        }}
        
        input:focus + .slider {{
            box-shadow: 0 0 1px #2196F3;
        }}
        
        input:checked + .slider:before {{
            transform: translateX(26px);
        }}
        
        /* Loading Skeleton */
        .skeleton {{
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 4px;
            height: 24px;
            margin-bottom: 8px;
        }}
        
        .dark-mode .skeleton {{
            background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
            background-size: 200% 100%;
        }}
        
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        .repo-link {{
            position: relative;
            display: inline-block;
            font-weight: 500;
            color: var(--primary-color);
            text-decoration: none;
            padding-bottom: 2px;
            transition: all 0.3s ease;
        }}
        
        .repo-link::after {{
            content: '';
            position: absolute;
            width: 100%;
            transform: scaleX(0);
            height: 2px;
            bottom: 0;
            left: 0;
            background-color: var(--primary-color);
            transform-origin: bottom right;
            transition: transform 0.3s ease-out;
        }}
        
        .repo-link:hover::after {{
            transform: scaleX(1);
            transform-origin: bottom left;
        }}
        
        .dark-mode .repo-link {{
            color: #4da3ff;
        }}
        
        .dark-mode .repo-link::after {{
            background-color: #4da3ff;
        }}
        
        .tooltip-inner {{
            max-width: 300px;
        }}
        
        .back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .back-to-top.visible {{
            opacity: 1;
            visibility: visible;
        }}
        
        .dark-mode .dataTables_wrapper .dataTables_length, 
        .dark-mode .dataTables_wrapper .dataTables_filter, 
        .dark-mode .dataTables_wrapper .dataTables_info, 
        .dark-mode .dataTables_wrapper .dataTables_processing, 
        .dark-mode .dataTables_wrapper .dataTables_paginate {{
            color: var(--dark-text);
        }}
        
        .dark-mode .dataTables_wrapper .dataTables_paginate .paginate_button {{
            color: var(--dark-text) !important;
        }}
        
        .dark-mode .dataTables_wrapper .dataTables_paginate .paginate_button.current {{
            color: white !important;
            background: var(--primary-color);
            border-color: var(--primary-color);
        }}
        
        .dark-mode .form-control, .dark-mode .form-select {{
            background-color: var(--dark-card-bg);
            border-color: var(--dark-border);
            color: var(--dark-text);
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
            .chart-container {{
                height: 300px;
            }}
        }}
        
        @media print {{
            .navbar, .theme-toggle, .back-to-top {{
                display: none !important;
            }}
            body {{
                background-color: white !important;
                color: black !important;
            }}
            .card {{
                break-inside: avoid;
                border: 1px solid #ddd;
                box-shadow: none !important;
            }}
            a {{
                text-decoration: underline;
                color: #000 !important;
            }}
            .card-header.bg-primary {{
                background-color: #f8f9fa !important;
                color: #000 !important;
            }}
            .header-section {{
                background: #f8f9fa !important;
                color: #000 !important;
            }}
        }}
        
        .repo-card {{
            height: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .repo-card::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(to right, #0d6efd, #0098ff);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }}
        
        .repo-card:hover::after {{
            transform: scaleX(1);
        }}
        
        .repo-card .card-body {{
            display: flex;
            flex-direction: column;
        }}
        
        .repo-metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 15px;
        }}
        
        .metric {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        
        .metric-icon {{
            width: 20px;
            margin-right: 8px;
            text-align: center;
        }}
        
        .metric-value {{
            font-variant-numeric: tabular-nums;
            font-weight: 500;
        }}
        
        .repo-card .card-footer {{
            margin-top: auto;
            border-top: none;
            background-color: transparent;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr); /* Fixed 4 columns layout */
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        @media (max-width: 992px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr); /* 2 columns on medium screens */
            }}
        }}
        
        @media (max-width: 576px) {{
            .stats-grid {{
                grid-template-columns: 1fr; /* 1 column on very small screens */
            }}
        }}
        
        @media (max-width: 768px) {{
            .repo-grid {{
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            }}
            
        }}
        
        .dark-mode .header-section {{
            background: linear-gradient(135deg, #1a4b8c 0%, #0a3d79 100%);
            color: #ffffff; /* Ensure pure white text for better contrast in dark mode */
        }}
        
        .dark-mode .header-section h1 {{
            color: #ffffff;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3); /* Add slight text shadow for better readability */
        }}
        
        .dark-mode .header-section p {{
            color: rgba(255, 255, 255, 0.95);
        }}
        
        .dark-mode .stats-icon {{
            background: linear-gradient(135deg, #4da3ff, #68b5ff);
            -webkit-background-clip: text;
        }}
        
        .dark-mode .stat-value {{
            color: var(--dark-text) !important;
        }}
        
        .dark-mode .stat-value.text-primary,
        .dark-mode .stat-value.text-success,
        .dark-mode .stat-value.text-info,
        .dark-mode .stat-value.text-danger,
        .dark-mode .stat-value.text-warning,
        .dark-mode .stat-value.text-secondary {{
            opacity: 0.9;
        }}
        
        .dark-mode .repo-card .description {{
            color: var(--dark-text);
        }}
        
        .dark-mode .metric-value {{
            color: var(--dark-text);
        }}
        
        .dark-mode .repo-card .card-header {{
            background-color: rgba(0, 0, 0, 0.2) !important;
        }}
        
        .dark-mode .filter-badge:not(.active) {{
            background-color: #444;
            color: var(--dark-text);
        }}
        
        /* UI Improvements */
        .repo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--secondary-color);
            background-color: rgba(0,0,0,0.02);
            border-radius: 12px;
            border: 1px dashed rgba(0,0,0,0.1);
            margin: 40px 0;
        }}
        
        .dark-mode .empty-state {{
            background-color: rgba(255,255,255,0.02);
            border-color: rgba(255,255,255,0.05);
            color: var(--dark-secondary-text);
        }}
        
        .empty-state i {{
            font-size: 3.5rem;
            margin-bottom: 20px;
            opacity: 0.6;
            color: var(--secondary-color);
        }}
        
        .dark-mode .empty-state i {{
            color: var(--dark-secondary-text);
        }}
        
        .repo-badge {{
            margin-bottom: 8px;
        }}
        
        .filter-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }}
        
        .repo-card {{
            display: flex;
            flex-direction: column;
        }}
        
        .repo-card .card-body {{
            flex: 1;
            padding: 1.5rem;
        }}
        
        .repo-card .card-header {{
            padding: 1rem 1.5rem;
        }}
        
        .footer {{
            margin-top: 4rem;
            padding: 2rem 0;
        }}
        
        .footer a {{
            font-weight: 500;
            text-decoration: none;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        /* Fix for Chrome rendering bug with grid items */
        @supports (-webkit-appearance:none) {{
            .stats-grid .card,
            .repo-grid .card {{
                transform: translateZ(0);
            }}
        }}
        
        /* Smoother loading for repository cards */
        .repo-grid .repo-card {{
            animation: fadeInUp 0.5s ease forwards;
            animation-delay: calc(0.05s * var(--card-index, 0));
            opacity: 0;
        }}
        
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Improve loading performance */
        .loading-optimization {{
            content-visibility: auto;
            contain-intrinsic-size: 0 500px;
        }}
        
        /* Fix for Safari flex gap issue */
        @media not all and (min-resolution:.001dpcm) {{ 
            .filter-buttons, .repo-metrics {{
                gap: 0;
            }}
            
            .filter-buttons .filter-badge {{
                margin-right: 8px;
            }}
            
            .repo-metrics .metric {{
                margin-right: 8px;
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
                <div class="theme-toggle ms-auto me-3 d-flex align-items-center">
                    <i class="bi bi-sun me-2"></i>
                    <label class="theme-switch mb-0">
                        <input type="checkbox" id="theme-toggle">
                        <span class="slider"></span>
                    </label>
                    <i class="bi bi-moon ms-2"></i>
                </div>
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
                            <a class="nav-link" href="https://github.com/{username}" target="_blank">
                                <i class="bi bi-box-arrow-up-right me-1"></i>GitHub Profile
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="header-section text-center animate__animated animate__fadeIn" id="overview">
            <img src="https://github.com/{username}.png" alt="{username}" class="avatar mb-3">
            <h1 class="display-4 mb-0">{username}</h1>
            <p class="lead">GitHub Repository Statistics</p>
            <div class="mt-4">
                <a href="https://github.com/{username}" class="btn btn-light me-2" target="_blank" aria-label="View GitHub Profile">
                    <i class="bi bi-github"></i> View Profile
                </a>
                <button class="btn btn-outline-light" id="share-button" aria-label="Share this report">
                    <i class="bi bi-share"></i> Share
                </button>
            </div>
        </div>
        
        <h2 class="mb-4 animate__animated animate__fadeInUp">Summary Statistics</h2>
        <div class="stats-grid animate__animated animate__fadeInUp">
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-star-fill"></i>
                    </div>
                    <div class="stat-value text-primary">
                        <span class="counter">{total_stars:,}</span>
                    </div>
                    <div class="stat-label">Total Stars</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-hdd-stack"></i>
                    </div>
                    <div class="stat-value text-success">
                        <span class="counter">{len(repositories):,}</span>
                    </div>
                    <div class="stat-label">Repositories</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-diagram-2"></i>
                    </div>
                    <div class="stat-value text-info">
                        <span class="counter">{total_forks:,}</span>
                    </div>
                    <div class="stat-label">Total Forks</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-git"></i>
                    </div>
                    <div class="stat-value text-danger">
                        <span class="counter">{total_commits:,}</span>
                    </div>
                    <div class="stat-label">Total Commits</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-people-fill"></i>
                    </div>
                    <div class="stat-value text-warning">
                        <span class="counter">{sum(r.get('contributors_count', 0) or 0 for r in repositories):,}</span>
                    </div>
                    <div class="stat-label">Total Contributors</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-check-circle"></i>
                    </div>
                    <div class="stat-value text-secondary">
                        <span class="counter">{total_closed_issues:,}</span>
                    </div>
                    <div class="stat-label">Closed Issues</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-hourglass-split"></i>
                    </div>
                    <div class="stat-value" style="color: #6f42c1;">
                        {avg_resolution_time_str}
                    </div>
                    <div class="stat-label">Avg Issue Resolution</div>
                </div>
            </div>
            
            <div class="card stats-card text-center">
                <div class="card-body">
                    <div class="stats-icon">
                        <i class="bi bi-clock-history"></i>
                    </div>
                    <div class="stat-value" style="color: #fd7e14;">
                        {repositories[0].get('last_update_str', 'Unknown') if repositories else 'N/A'}
                    </div>
                    <div class="stat-label">Latest Update</div>
                </div>
            </div>
        </div>
        
        <h2 class="mb-4 mt-5 animate__animated animate__fadeInUp" id="repositories">
            All Repositories
            <span class="badge bg-primary repo-count-badge">{len(repositories)}</span>
        </h2>
        
        <div class="search-container animate__animated animate__fadeInUp">
            <div class="input-group mb-3">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input type="text" class="form-control" id="repo-search" placeholder="Search repositories by name or description...">
            </div>
            
            <div class="filter-buttons mb-3">
                <span class="badge bg-secondary filter-badge active" data-filter="all">All</span>
                <span class="badge bg-secondary filter-badge" data-filter="stars">Most Stars</span>
                <span class="badge bg-secondary filter-badge" data-filter="forks">Most Forks</span>
                <span class="badge bg-secondary filter-badge" data-filter="recent">Recently Updated</span>
                <span class="badge bg-secondary filter-badge" data-filter="commits">Most Commits</span>
            </div>
        </div>
        
        <div class="repo-grid animate__animated animate__fadeInUp" id="repository-grid">
    """
    
    # Add all repositories as cards
    sorted_repos = sorted(repositories, key=lambda r: r.get('stars', 0) or 0, reverse=True)
    
    for repo in sorted_repos:
        repo_name = repo.get('name', 'N/A')
        repo_url = repo.get('url', '#')
        description = repo.get('description', 'No description available')
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
        
        html_content += f"""
            <div class="card repo-card" 
                data-name="{repo_name.lower()}" 
                data-description="{description.lower()}" 
                data-stars="{stars}" 
                data-forks="{forks}" 
                data-commits="{commits if commits is not None else 0}" 
                data-update="{last_update}">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">
                        <a href="{repo_url}" class="repo-link" target="_blank">{repo_name}</a>
                    </h5>
                </div>
                <div class="card-body">
                    <p class="description">{description}</p>
                    
                    <div class="d-flex flex-wrap mb-3">
                        <span class="repo-badge">
                            <i class="bi bi-star-fill text-warning"></i> {stars:,}
                        </span>
                        <span class="repo-badge">
                            <i class="bi bi-diagram-2 text-primary"></i> {forks:,}
                        </span>
                        <span class="repo-badge">
                            <i class="bi bi-git text-danger"></i> {commits_str}
                        </span>
                    </div>
                    
                    <div class="repo-metrics">
                        <div class="metric">
                            <div class="metric-icon">
                                <i class="bi bi-people-fill text-success"></i>
                            </div>
                            <div class="metric-value">
                                {contributors_str} contributors
                            </div>
                        </div>
                        
                        <div class="metric">
                            <div class="metric-icon">
                                <i class="bi bi-check-circle text-info"></i>
                            </div>
                            <div class="metric-value">
                                {closed_issues_str} issues closed
                            </div>
                        </div>
                        
                        <div class="metric">
                            <div class="metric-icon">
                                <i class="bi bi-clock text-secondary"></i>
                            </div>
                            <div class="metric-value">
                                Updated {last_update}
                            </div>
                        </div>
                        
                        <div class="metric">
                            <div class="metric-icon">
                                <i class="bi bi-hourglass-split" style="color: #6f42c1;"></i>
                            </div>
                            <div class="metric-value">
                                {resolution_time} avg resolution
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """
    
    # Add empty state for when no repositories match search
    html_content += """
            <div class="empty-state" id="empty-state" style="display:none;">
                <i class="bi bi-search"></i>
                <h4>No repositories found</h4>
                <p>Try adjusting your search or filters</p>
            </div>
        </div>
        
        <footer class="footer text-center mt-5">
            <div class="container">
                <p class="mb-0">
                    Made with ❤️ by <a href="https://github.com/fabriziosalmi" target="_blank">fab</a> with 
                    <a href="https://github.com/{username}/repos" target="_blank">GitHub Stats Generator</a>
                </p>
            </div>
        </footer>
    </div>
    
    <a href="#" class="back-to-top" id="back-to-top" aria-label="Back to top">
        <i class="bi bi-arrow-up"></i>
    </a>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/countup.js@2.0.7/dist/countUp.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Improved theme toggle functionality
            const themeToggle = document.getElementById('theme-toggle');
            const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
            const savedTheme = localStorage.getItem('theme');
            
            // Function to apply theme
            function applyTheme(isDark) {
                if (isDark) {
                    document.body.classList.add('dark-mode');
                    if (themeToggle) themeToggle.checked = true;
                    
                    // Fix specific color elements that need special handling
                    document.querySelectorAll('.stat-value').forEach(el => {
                        // Preserve the color class but make it more visible in dark mode
                        if (el.classList.contains('text-primary') || 
                            el.classList.contains('text-success') ||
                            el.classList.contains('text-info') ||
                            el.classList.contains('text-warning') ||
                            el.classList.contains('text-danger') ||
                            el.classList.contains('text-secondary')) {
                            el.style.opacity = '0.9';
                        }
                    });
                } else {
                    document.body.classList.remove('dark-mode');
                    if (themeToggle) themeToggle.checked = false;
                    
                    // Reset styles when switching back to light mode
                    document.querySelectorAll('.stat-value').forEach(el => {
                        el.style.opacity = '';
                    });
                }
            }
            
            // Apply initial theme based on preference or system setting
            if (savedTheme === 'dark') {
                applyTheme(true);
            } else if (savedTheme === 'light') {
                applyTheme(false);
            } else {
                // No saved preference, use system preference
                applyTheme(prefersDarkScheme.matches);
            }
            
            // Listen for changes to system color scheme
            prefersDarkScheme.addEventListener('change', function(event) {
                // Only update based on system changes if user hasn't set preference
                if (!localStorage.getItem('theme')) {
                    applyTheme(event.matches);
                }
            });
            
            // Handle toggle switch changes
            if (themeToggle) {
                themeToggle.addEventListener('change', function() {
                    if (this.checked) {
                        applyTheme(true);
                        localStorage.setItem('theme', 'dark');
                    } else {
                        applyTheme(false);
                        localStorage.setItem('theme', 'light');
                    }
                });
            }
            
            // Debug info for theme settings
            console.log({
                'System prefers dark': prefersDarkScheme.matches,
                'Saved theme': savedTheme || 'none',
                'Applied theme': document.body.classList.contains('dark-mode') ? 'dark' : 'light'
            });
            
            // Back to top button
            const backToTopButton = document.getElementById('back-to-top');
            
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300) {
                    backToTopButton.classList.add('visible');
                } else {
                    backToTopButton.classList.remove('visible');
                }
            });
            
            backToTopButton.addEventListener('click', function(e) {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            
            // Repository search functionality
            const searchInput = document.getElementById('repo-search');
            const repoCards = document.querySelectorAll('.repo-card');
            const emptyState = document.getElementById('empty-state');
            
            searchInput.addEventListener('input', filterRepositories);
            
            function filterRepositories() {
                const searchTerm = searchInput.value.toLowerCase().trim();
                const activeFilter = document.querySelector('.filter-badge.active').getAttribute('data-filter');
                let visibleCount = 0;
                
                repoCards.forEach(card => {
                    const name = card.getAttribute('data-name');
                    const description = card.getAttribute('data-description');
                    const isMatch = name.includes(searchTerm) || description.includes(searchTerm);
                    
                    if (isMatch) {
                        card.style.display = 'block';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // Show/hide empty state
                emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
            }
            
            // Filter buttons
            const filterButtons = document.querySelectorAll('.filter-badge');
            
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Update active state
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    const filterType = this.getAttribute('data-filter');
                    sortRepositories(filterType);
                });
            });
            
            function sortRepositories(filterType) {
                const grid = document.getElementById('repository-grid');
                const cards = Array.from(document.querySelectorAll('.repo-card'));
                
                // Sort cards based on filter type
                switch(filterType) {
                    case 'stars':
                        cards.sort((a, b) => parseInt(b.getAttribute('data-stars')) - parseInt(a.getAttribute('data-stars')));
                        break;
                    case 'forks':
                        cards.sort((a, b) => parseInt(b.getAttribute('data-forks')) - parseInt(a.getAttribute('data-forks')));
                        break;
                    case 'commits':
                        cards.sort((a, b) => parseInt(b.getAttribute('data-commits')) - parseInt(a.getAttribute('data-commits')));
                        break;
                    case 'recent':
                        // This is a simple string comparison which works for dates in "X days/months ago" format
                        cards.sort((a, b) => a.getAttribute('data-update').localeCompare(b.getAttribute('data-update')));
                        break;
                    case 'all':
                    default:
                        // Default sort by stars
                        cards.sort((a, b) => parseInt(b.getAttribute('data-stars')) - parseInt(a.getAttribute('data-stars')));
                        break;
                }
                
                // Remove all cards and re-add in sorted order
                cards.forEach(card => grid.appendChild(card));
                
                // Reapply search filter
                filterRepositories();
            }
            
            // Share button functionality
            document.getElementById('share-button').addEventListener('click', function() {
                if (navigator.share) {
                    navigator.share({
                        title: 'GitHub Stats for {username}',
                        text: 'Check out {username}\\'s GitHub statistics',
                        url: window.location.href
                    })
                    .catch(console.error);
                } else {
                    // Fallback for browsers that don't support navigator.share
                    const dummy = document.createElement('input');
                    document.body.appendChild(dummy);
                    dummy.value = window.location.href;
                    dummy.select();
                    document.execCommand('copy');
                    document.body.removeChild(dummy);
                    
                    alert('URL copied to clipboard!');
                }
            });
            
            // Initialize CountUp.js for stat numbers
            document.querySelectorAll('.counter').forEach(element => {
                const value = parseInt(element.innerText.replace(/,/g, ''));
                const countUp = new CountUp(element, value, {
                    duration: 2.5,
                    separator: ',',
                });
                countUp.start();
            });
            
            // Add animation delay to repository cards for staggered entrance
            document.querySelectorAll('.repo-card').forEach((card, index) => {
                card.style.setProperty('--card-index', index);
            });
            
            // Fix for empty state responsiveness
            function updateEmptyStateHeight() {
                const emptyState = document.getElementById('empty-state');
                const grid = document.getElementById('repository-grid');
                if (emptyState && grid) {
                    if (emptyState.style.display === 'block') {
                        emptyState.style.minHeight = grid.offsetHeight > 400 ? 
                                                    (grid.offsetHeight * 0.7) + 'px' : 
                                                    '400px';
                    }
                }
            }
            
            const observer = new ResizeObserver(updateEmptyStateHeight);
            const grid = document.getElementById('repository-grid');
            if (grid) observer.observe(grid);
            
            // Enhance search behavior for better UX
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(filterRepositories, 200); // Debounce search
            });
            
            // Add proper error handling for CountUp.js
            document.querySelectorAll('.counter').forEach(element => {
                try {
                    const valueText = element.innerText.replace(/,/g, '');
                    const value = parseInt(valueText);
                    
                    if (!isNaN(value)) {
                        const countUp = new CountUp(element, value, {
                            duration: 2.5,
                            separator: ',',
                        });
                        
                        if (!countUp.error) {
                            countUp.start();
                        } else {
                            console.error("CountUp error: ", countUp.error);
                        }
                    }
                } catch (err) {
                    console.error("Error initializing counter:", err);
                }
            });
            
        });
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
