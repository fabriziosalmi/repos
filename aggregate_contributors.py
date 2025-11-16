"""
Aggregate contributor statistics across all repositories
Generates cross-project contributor analytics for Aegis Module 3.1
"""

import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any


def aggregate_contributor_stats(repos_data_path: str, output_path: str):
    """
    Aggregate contributor data from all repositories
    
    Args:
        repos_data_path: Path to repositories-data.json
        output_path: Path to save contributor-stats.json
    """
    
    with open(repos_data_path, 'r') as f:
        repos = json.load(f)
    
    # Aggregate contributor stats
    contributors = defaultdict(lambda: {
        'login': '',
        'avatar_url': '',
        'profile_url': '',
        'total_contributions': 0,
        'repositories': [],
        'first_contribution': None,
        'last_contribution': None,
        'languages': set(),
        'total_stars': 0,
        'total_forks': 0,
    })
    
    # Repositories metadata
    repo_metadata = []
    
    for repo in repos:
        repo_name = repo.get('name', '')
        repo_url = repo.get('url', '')
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        language = repo.get('language', 'Unknown')
        last_update = repo.get('last_update', '')
        
        repo_metadata.append({
            'name': repo_name,
            'url': repo_url,
            'stars': stars,
            'forks': forks,
            'language': language,
            'last_update': last_update
        })
        
        # Process contributors for this repo
        repo_contributors = repo.get('contributors', [])
        
        for contributor in repo_contributors:
            login = contributor.get('login', 'unknown')
            
            if login == 'unknown':
                continue
            
            contributions = contributor.get('contributions', 0)
            avatar = contributor.get('avatar_url', '')
            profile = contributor.get('profile_url', f'https://github.com/{login}')
            
            # Update aggregated data
            contributors[login]['login'] = login
            contributors[login]['avatar_url'] = avatar
            contributors[login]['profile_url'] = profile
            contributors[login]['total_contributions'] += contributions
            contributors[login]['total_stars'] += stars
            contributors[login]['total_forks'] += forks
            contributors[login]['languages'].add(language)
            
            # Track repository participation
            contributors[login]['repositories'].append({
                'name': repo_name,
                'url': repo_url,
                'contributions': contributions,
                'stars': stars,
                'language': language
            })
            
            # Update contribution dates
            if last_update:
                if not contributors[login]['last_contribution'] or \
                   last_update > contributors[login]['last_contribution']:
                    contributors[login]['last_contribution'] = last_update
                
                if not contributors[login]['first_contribution'] or \
                   last_update < contributors[login]['first_contribution']:
                    contributors[login]['first_contribution'] = last_update
    
    # Convert to list and sort by total contributions
    contributor_list = []
    
    for login, data in contributors.items():
        contributor_list.append({
            'login': data['login'],
            'avatar_url': data['avatar_url'],
            'profile_url': data['profile_url'],
            'total_contributions': data['total_contributions'],
            'total_repositories': len(data['repositories']),
            'repositories': sorted(data['repositories'], key=lambda x: x['contributions'], reverse=True),
            'first_contribution': data['first_contribution'],
            'last_contribution': data['last_contribution'],
            'languages': list(data['languages']),
            'total_stars': data['total_stars'],
            'total_forks': data['total_forks'],
            'impact_score': calculate_impact_score(data)
        })
    
    # Sort by total contributions
    contributor_list.sort(key=lambda x: x['total_contributions'], reverse=True)
    
    # Identify newcomers (contributors with recent first contribution)
    now = datetime.now()
    newcomers = []
    
    for contributor in contributor_list:
        if contributor['first_contribution']:
            first_date = datetime.fromisoformat(contributor['first_contribution'].replace('Z', '+00:00'))
            days_since_first = (now - first_date.replace(tzinfo=None)).days
            
            if days_since_first <= 30:  # Last 30 days
                newcomers.append({
                    **contributor,
                    'days_since_first': days_since_first
                })
    
    # Compile output
    output_data = {
        'updated_at': datetime.now().isoformat(),
        'total_contributors': len(contributor_list),
        'total_repositories': len(repo_metadata),
        'top_contributors': contributor_list[:50],  # Top 50
        'newcomers': newcomers[:20],  # Top 20 newcomers
        'all_contributors': contributor_list,
        'repositories': repo_metadata,
        'statistics': {
            'avg_contributions_per_contributor': sum(c['total_contributions'] for c in contributor_list) / len(contributor_list) if contributor_list else 0,
            'avg_repos_per_contributor': sum(c['total_repositories'] for c in contributor_list) / len(contributor_list) if contributor_list else 0,
            'total_contributions': sum(c['total_contributions'] for c in contributor_list),
        }
    }
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Contributor stats saved to {output_path}")
    print(f"📊 Total contributors: {len(contributor_list)}")
    print(f"🆕 Newcomers (last 30 days): {len(newcomers)}")
    if contributor_list:
        print(f"🏆 Top contributor: {contributor_list[0]['login']} ({contributor_list[0]['total_contributions']} contributions)")
    else:
        print("ℹ️  No contributors found in the data")


def calculate_impact_score(contributor_data: Dict[str, Any]) -> float:
    """
    Calculate contributor impact score based on:
    - Total contributions
    - Number of repositories
    - Total stars across contributed repos
    - Language diversity
    """
    contributions = contributor_data['total_contributions']
    repos = len(contributor_data['repositories'])
    stars = contributor_data['total_stars']
    languages = len(contributor_data['languages'])
    
    # Weighted score
    score = (
        contributions * 1.0 +
        repos * 5.0 +
        stars * 0.1 +
        languages * 2.0
    )
    
    return round(score, 2)


if __name__ == '__main__':
    import sys
    
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'docs/repositories-data.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'docs/contributor-stats.json'
    
    aggregate_contributor_stats(input_path, output_path)
