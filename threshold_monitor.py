#!/usr/bin/env python3
"""
Aegis Threshold Monitor - Real-time Milestone & Alert Detection
Compares current data with previous state to detect significant changes
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple
import requests
from datetime import datetime

class ThresholdMonitor:
    # Milestone thresholds for stars
    STAR_MILESTONES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
    
    # Health score thresholds
    HEALTH_CRITICAL = 40
    HEALTH_WARNING = 60
    
    def __init__(self, current_data_path: str, previous_data_path: str = None):
        self.current_repos = self._load_json(current_data_path)
        self.previous_repos = self._load_json(previous_data_path) if previous_data_path else []
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL') or os.getenv('SLACK_WEBHOOK_URL')
        
        # Create lookup for previous data
        self.previous_map = {repo['name']: repo for repo in self.previous_repos}
    
    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        """Load JSON data safely"""
        if not path or not os.path.exists(path):
            return []
        
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}")
            return []
    
    def detect_star_milestones(self) -> List[Dict[str, Any]]:
        """Detect repositories that crossed star milestones"""
        milestones_reached = []
        
        for repo in self.current_repos:
            name = repo['name']
            current_stars = repo['stars']
            previous_stars = self.previous_map.get(name, {}).get('stars', 0)
            
            # Check which milestones were crossed
            for milestone in self.STAR_MILESTONES:
                if previous_stars < milestone <= current_stars:
                    milestones_reached.append({
                        'repo': name,
                        'url': repo['url'],
                        'milestone': milestone,
                        'current_stars': current_stars,
                        'previous_stars': previous_stars,
                        'gained': current_stars - previous_stars
                    })
        
        return milestones_reached
    
    def detect_health_degradation(self) -> List[Dict[str, Any]]:
        """Detect significant health score drops"""
        degradations = []
        
        for repo in self.current_repos:
            name = repo['name']
            current_health = repo.get('issue_health', {}).get('health_score', 100)
            previous_health = self.previous_map.get(name, {}).get('issue_health', {}).get('health_score', 100)
            
            # Significant drop (>20 points) or crossing critical threshold
            drop = previous_health - current_health
            
            if drop > 20 or (previous_health > self.HEALTH_CRITICAL >= current_health):
                degradations.append({
                    'repo': name,
                    'url': repo['url'],
                    'current_health': current_health,
                    'previous_health': previous_health,
                    'drop': drop,
                    'status': repo.get('issue_health', {}).get('status', 'unknown')
                })
        
        return degradations
    
    def detect_new_repositories(self) -> List[Dict[str, Any]]:
        """Detect newly added repositories"""
        new_repos = []
        previous_names = set(self.previous_map.keys())
        
        for repo in self.current_repos:
            if repo['name'] not in previous_names:
                new_repos.append({
                    'repo': repo['name'],
                    'url': repo['url'],
                    'stars': repo['stars'],
                    'language': repo.get('language', 'Unknown'),
                    'description': repo.get('description', 'No description')
                })
        
        return new_repos
    
    def detect_momentum_spikes(self) -> List[Dict[str, Any]]:
        """Detect sudden momentum increases"""
        spikes = []
        
        for repo in self.current_repos:
            name = repo['name']
            momentum = repo.get('momentum', {})
            current_score = momentum.get('score', 0)
            
            # Previous momentum (default to 0 if not available)
            prev_momentum = self.previous_map.get(name, {}).get('momentum', {}).get('score', 0)
            
            # Spike detection: score increase > 50 points
            if current_score - prev_momentum > 50:
                spikes.append({
                    'repo': name,
                    'url': repo['url'],
                    'momentum_score': current_score,
                    'stars_gained_7d': momentum.get('stars_7d', 0),
                    'trend': momentum.get('trend', 'unknown')
                })
        
        return spikes
    
    def format_discord_message(self, alerts: Dict[str, List]) -> Dict[str, Any]:
        """Format alerts for Discord webhook"""
        embeds = []
        
        # Star Milestones
        if alerts['milestones']:
            milestone_text = "\n".join([
                f"🎉 **[{a['repo']}]({a['url']})** reached **{a['milestone']}** stars! "
                f"(+{a['gained']} since last update)"
                for a in alerts['milestones'][:5]
            ])
            
            embeds.append({
                "title": "⭐ Star Milestones Reached",
                "description": milestone_text,
                "color": 0xFFD700,  # Gold
                "timestamp": datetime.now().isoformat()
            })
        
        # Health Degradation
        if alerts['health_degradation']:
            health_text = "\n".join([
                f"⚠️ **[{a['repo']}]({a['url']})** health dropped to {a['current_health']:.0f} "
                f"(-{a['drop']:.0f} points)"
                for a in alerts['health_degradation'][:5]
            ])
            
            embeds.append({
                "title": "🚨 Health Alerts",
                "description": health_text,
                "color": 0xFF4500,  # Red-Orange
                "timestamp": datetime.now().isoformat()
            })
        
        # New Repositories
        if alerts['new_repos']:
            new_text = "\n".join([
                f"✨ **[{a['repo']}]({a['url']})** ({a['language']}) - {a['stars']} stars"
                for a in alerts['new_repos'][:5]
            ])
            
            embeds.append({
                "title": "🆕 New Repositories",
                "description": new_text,
                "color": 0x00FF00,  # Green
                "timestamp": datetime.now().isoformat()
            })
        
        # Momentum Spikes
        if alerts['momentum_spikes']:
            spike_text = "\n".join([
                f"🚀 **[{a['repo']}]({a['url']})** momentum spike! "
                f"Score: {a['momentum_score']:.0f} (+{a['stars_gained_7d']} stars/7d)"
                for a in alerts['momentum_spikes'][:5]
            ])
            
            embeds.append({
                "title": "📈 Momentum Spikes",
                "description": spike_text,
                "color": 0x00FFCC,  # Cyan
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "content": "🛡️ **AEGIS Threshold Alert**",
            "embeds": embeds
        }
    
    def send_webhook(self, payload: Dict[str, Any]) -> bool:
        """Send alert to webhook"""
        if not self.webhook_url:
            print("No webhook URL configured")
            return False
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print("✅ Alert sent to webhook")
            return True
        except Exception as e:
            print(f"❌ Failed to send webhook: {e}")
            return False
    
    def run(self) -> Dict[str, List]:
        """Execute threshold monitoring"""
        print("🛡️ AEGIS Threshold Monitor - Analyzing Changes...\n")
        
        # Detect all alert types
        alerts = {
            'milestones': self.detect_star_milestones(),
            'health_degradation': self.detect_health_degradation(),
            'new_repos': self.detect_new_repositories(),
            'momentum_spikes': self.detect_momentum_spikes()
        }
        
        # Print summary
        total_alerts = sum(len(v) for v in alerts.values())
        print(f"📊 Detection Summary:")
        print(f"   - Star Milestones: {len(alerts['milestones'])}")
        print(f"   - Health Degradation: {len(alerts['health_degradation'])}")
        print(f"   - New Repositories: {len(alerts['new_repos'])}")
        print(f"   - Momentum Spikes: {len(alerts['momentum_spikes'])}")
        print(f"   Total Alerts: {total_alerts}\n")
        
        # Send alerts if any detected
        if total_alerts > 0:
            payload = self.format_discord_message(alerts)
            self.send_webhook(payload)
            
            # Print details
            for alert_type, items in alerts.items():
                if items:
                    print(f"\n{alert_type.upper()}:")
                    for item in items:
                        print(f"  - {item}")
        else:
            print("✅ No alerts detected - all systems nominal")
        
        return alerts

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AEGIS Threshold Monitor')
    parser.add_argument('--current', required=True, help='Path to current repository data')
    parser.add_argument('--previous', help='Path to previous repository data')
    
    args = parser.parse_args()
    
    monitor = ThresholdMonitor(args.current, args.previous)
    monitor.run()
