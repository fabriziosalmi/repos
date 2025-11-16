#!/usr/bin/env python3
"""
Aegis Reporter - Weekly Repository Activity Summary
Generates comprehensive weekly reports and sends via email/webhook
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
import requests

class AegisReporter:
    def __init__(self, data_path: str = 'docs/repositories-data.json'):
        self.data_path = data_path
        self.repos = self._load_data()
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL') or os.getenv('SLACK_WEBHOOK_URL')
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.recipient_email = os.getenv('REPORT_EMAIL')
        
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load repository data from JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.data_path} not found")
            sys.exit(1)
    
    def get_top_star_gainers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Identify repositories with highest star growth"""
        star_gainers = []
        
        for repo in self.repos:
            momentum = repo.get('momentum', {})
            stars_gained = momentum.get('stars_7d', 0)
            
            if stars_gained > 0:
                star_gainers.append({
                    'name': repo['name'],
                    'stars': repo['stars'],
                    'gained_7d': stars_gained,
                    'gained_30d': momentum.get('stars_30d', 0),
                    'momentum_score': momentum.get('score', 0),
                    'url': repo['url']
                })
        
        # Sort by 7-day star gain
        star_gainers.sort(key=lambda x: x['gained_7d'], reverse=True)
        return star_gainers[:limit]
    
    def get_stale_projects(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
        """Find projects with no recent activity"""
        stale = []
        threshold_date = datetime.now()
        
        for repo in self.repos:
            try:
                # Parse ISO format and make naive for comparison
                last_update_str = repo['last_update'].replace('Z', '+00:00')
                last_update = datetime.fromisoformat(last_update_str)
                
                # Make both datetimes naive for comparison
                if last_update.tzinfo is not None:
                    last_update = last_update.replace(tzinfo=None)
                
                days_since_update = (threshold_date - last_update).days
                
                if days_since_update > days_threshold:
                    stale.append({
                        'name': repo['name'],
                        'last_update': repo['last_update'],
                        'days_stale': days_since_update,
                        'stars': repo['stars'],
                        'url': repo['url']
                    })
            except Exception as e:
                print(f"Warning: Could not parse date for {repo['name']}: {e}")
                continue
        
        # Sort by staleness
        stale.sort(key=lambda x: x['days_stale'], reverse=True)
        return stale
    
    def get_health_degradation(self) -> List[Dict[str, Any]]:
        """Identify projects with declining health scores"""
        degraded = []
        
        for repo in self.repos:
            health = repo.get('issue_health', {})
            status = health.get('status', 'unknown')
            
            if status in ['needs_attention', 'moderate']:
                degraded.append({
                    'name': repo['name'],
                    'health_score': health.get('health_score', 0),
                    'status': status,
                    'stale_issues': health.get('stale_issues_count', 0),
                    'avg_response_hours': health.get('avg_response_hours', 0),
                    'url': repo['url']
                })
        
        # Sort by health score (worst first)
        degraded.sort(key=lambda x: x['health_score'])
        return degraded
    
    def get_critical_bus_factors(self) -> List[Dict[str, Any]]:
        """Find projects with critical bus factor"""
        critical = []
        
        for repo in self.repos:
            bus_factor = repo.get('bus_factor', {})
            risk_level = bus_factor.get('risk_level', 'unknown')
            
            if risk_level == 'critical':
                critical.append({
                    'name': repo['name'],
                    'bus_factor': bus_factor.get('bus_factor', 0),
                    'risk_level': risk_level,
                    'stars': repo['stars'],
                    'url': repo['url']
                })
        
        return critical
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Calculate overall portfolio statistics"""
        total_repos = len(self.repos)
        total_stars = sum(repo['stars'] for repo in self.repos)
        total_forks = sum(repo['forks'] for repo in self.repos)
        
        # Language distribution
        languages = defaultdict(int)
        for repo in self.repos:
            lang = repo.get('language', 'Unknown')
            languages[lang] += 1
        
        # Health distribution
        health_dist = defaultdict(int)
        for repo in self.repos:
            status = repo.get('issue_health', {}).get('status', 'unknown')
            health_dist[status] += 1
        
        return {
            'total_repos': total_repos,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'avg_stars': total_stars // total_repos if total_repos > 0 else 0,
            'languages': dict(languages),
            'health_distribution': dict(health_dist)
        }
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive Markdown report"""
        report_date = datetime.now().strftime('%Y-%m-%d')
        
        # Gather all data
        top_gainers = self.get_top_star_gainers()
        stale_projects = self.get_stale_projects()
        health_issues = self.get_health_degradation()
        bus_factor_critical = self.get_critical_bus_factors()
        summary = self.get_summary_stats()
        
        # Build report
        report = f"""# 🛡️ AEGIS Weekly Report
**Report Date**: {report_date}

---

## 📊 Portfolio Overview

- **Total Repositories**: {summary['total_repos']}
- **Total Stars**: ⭐ {summary['total_stars']:,}
- **Total Forks**: 🍴 {summary['total_forks']:,}
- **Average Stars per Repo**: {summary['avg_stars']}

### Health Distribution
"""
        
        for status, count in summary['health_distribution'].items():
            emoji = '✅' if status == 'healthy' else '⚠️' if status == 'moderate' else '🚨'
            report += f"- {emoji} **{status.replace('_', ' ').title()}**: {count} repos\n"
        
        # Top Star Gainers
        if top_gainers:
            report += "\n---\n\n## 🚀 Top Star Gainers (Last 7 Days)\n\n"
            for i, repo in enumerate(top_gainers, 1):
                report += f"### {i}. [{repo['name']}]({repo['url']})\n"
                report += f"- **Current Stars**: ⭐ {repo['stars']:,}\n"
                report += f"- **Gained (7d)**: +{repo['gained_7d']} stars\n"
                report += f"- **Gained (30d)**: +{repo['gained_30d']} stars\n"
                report += f"- **Momentum Score**: {repo['momentum_score']:.1f}/100\n\n"
        
        # Stale Projects
        if stale_projects:
            report += "\n---\n\n## 🕸️ Stale Projects (No Activity)\n\n"
            report += f"*Projects with no updates in the last 90+ days*\n\n"
            for repo in stale_projects[:5]:
                report += f"- **[{repo['name']}]({repo['url']})**: {repo['days_stale']} days since last update\n"
        
        # Health Degradation
        if health_issues:
            report += "\n---\n\n## ⚠️ Health Alerts\n\n"
            report += "*Projects requiring attention*\n\n"
            for repo in health_issues[:5]:
                status_emoji = '🚨' if repo['status'] == 'needs_attention' else '⚠️'
                report += f"### {status_emoji} [{repo['name']}]({repo['url']})\n"
                report += f"- **Health Score**: {repo['health_score']:.0f}/100\n"
                report += f"- **Status**: {repo['status'].replace('_', ' ').title()}\n"
                report += f"- **Stale Issues**: {repo['stale_issues']}\n"
                report += f"- **Avg Response Time**: {repo['avg_response_hours']:.1f}h\n\n"
        
        # Critical Bus Factors
        if bus_factor_critical:
            report += "\n---\n\n## 🚨 Critical Bus Factor Alerts\n\n"
            report += "*Projects dependent on single contributors*\n\n"
            for repo in bus_factor_critical:
                report += f"- **[{repo['name']}]({repo['url']})**: Bus Factor = {repo['bus_factor']} (⭐ {repo['stars']} stars)\n"
        
        # Call to Action
        report += "\n---\n\n## 🎯 Recommended Actions\n\n"
        
        if health_issues:
            report += "1. **Address Health Issues**: Review and respond to issues in projects marked with ⚠️\n"
        
        if stale_projects:
            report += "2. **Revive Stale Projects**: Consider archiving or planning updates for inactive repos\n"
        
        if bus_factor_critical:
            report += "3. **Distribute Workload**: Seek additional contributors for critical single-maintainer projects\n"
        
        if top_gainers:
            report += "4. **Celebrate Success**: Share achievements of top-performing projects on social media\n"
        
        report += "\n---\n\n*Generated by AEGIS - Your Proactive Intelligence System*\n"
        
        return report
    
    def send_to_webhook(self, message: str) -> bool:
        """Send report to Discord/Slack webhook"""
        if not self.webhook_url:
            print("No webhook URL configured")
            return False
        
        try:
            # Format for Discord/Slack
            payload = {
                "content": "📊 **AEGIS Weekly Report**",
                "embeds": [{
                    "title": "Weekly Repository Activity Summary",
                    "description": message[:2000],  # Truncate for embed limits
                    "color": 0x00ffcc,
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            print("✅ Report sent to webhook successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send webhook: {e}")
            return False
    
    def send_email(self, report: str) -> bool:
        """Send report via SendGrid email"""
        if not self.sendgrid_api_key or not self.recipient_email:
            print("SendGrid not configured")
            return False
        
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            # Convert Markdown to basic HTML
            html_content = f"<pre style='font-family: monospace;'>{report}</pre>"
            
            data = {
                "personalizations": [{
                    "to": [{"email": self.recipient_email}],
                    "subject": f"🛡️ AEGIS Weekly Report - {datetime.now().strftime('%Y-%m-%d')}"
                }],
                "from": {"email": "aegis@yourdomain.com", "name": "AEGIS Reporter"},
                "content": [
                    {"type": "text/plain", "value": report},
                    {"type": "text/html", "value": html_content}
                ]
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print("✅ Email sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def run(self, output_file: str = None):
        """Generate and distribute weekly report"""
        print("🛡️ AEGIS Reporter - Generating Weekly Summary...\n")
        
        # Generate report
        report = self.generate_markdown_report()
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"✅ Report saved to {output_file}")
        
        # Print to console
        print("\n" + "="*80)
        print(report)
        print("="*80 + "\n")
        
        # Send notifications
        webhook_sent = self.send_to_webhook(report)
        email_sent = self.send_email(report)
        
        if webhook_sent or email_sent:
            print("\n✅ Report distributed successfully!")
        else:
            print("\n⚠️ Report generated but not distributed (configure webhooks/email)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AEGIS Weekly Reporter')
    parser.add_argument('--data', default='docs/repositories-data.json', help='Path to repository data JSON')
    parser.add_argument('--output', help='Output file path for Markdown report')
    
    args = parser.parse_args()
    
    reporter = AegisReporter(data_path=args.data)
    reporter.run(output_file=args.output)
