"""
Aegis Label Helper - Serverless Function
Manages GitHub issue labels via GitHub API with write permissions
"""

import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import requests


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function to manage GitHub labels
    
    Endpoints:
    - GET /api/labels?repo=owner/name - List available labels
    - POST /api/labels - Add label to issue
      Body: {repo: "owner/name", issue: 123, labels: ["bug", "help wanted"]}
    - DELETE /api/labels - Remove label from issue
      Body: {repo: "owner/name", issue: 123, label: "bug"}
    """
    
    def _set_headers(self, status=200):
        """Set CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _get_github_token(self):
        """Get GitHub token from environment"""
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
        return token
    
    def _make_github_request(self, method, url, data=None):
        """Make authenticated request to GitHub API"""
        headers = {
            'Authorization': f'token {self._get_github_token()}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Aegis-Label-Helper'
        }
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        response.raise_for_status()
        return response.json() if response.text else {}
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers()
    
    def do_GET(self):
        """Get available labels for a repository"""
        try:
            # Parse query parameters
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            params = parse_qs(query_string)
            repo = params.get('repo', [''])[0]
            
            if not repo or '/' not in repo:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Repository parameter required (format: owner/name)'
                }).encode())
                return
            
            # Fetch labels from GitHub
            url = f'https://api.github.com/repos/{repo}/labels'
            labels = self._make_github_request('GET', url)
            
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'labels': [
                    {
                        'name': label['name'],
                        'color': label['color'],
                        'description': label.get('description', '')
                    }
                    for label in labels
                ]
            }).encode())
            
        except requests.exceptions.HTTPError as e:
            self._set_headers(e.response.status_code)
            self.wfile.write(json.dumps({
                'error': f'GitHub API error: {str(e)}'
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': f'Server error: {str(e)}'
            }).encode())
    
    def do_POST(self):
        """Add labels to an issue"""
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            repo = data.get('repo')
            issue = data.get('issue')
            labels = data.get('labels', [])
            
            if not repo or not issue or not labels:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing required fields: repo, issue, labels'
                }).encode())
                return
            
            # Add labels via GitHub API
            url = f'https://api.github.com/repos/{repo}/issues/{issue}/labels'
            result = self._make_github_request('POST', url, {'labels': labels})
            
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': f'Added {len(labels)} label(s) to issue #{issue}',
                'labels': [label['name'] for label in result]
            }).encode())
            
        except requests.exceptions.HTTPError as e:
            self._set_headers(e.response.status_code)
            self.wfile.write(json.dumps({
                'error': f'GitHub API error: {str(e)}'
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': f'Server error: {str(e)}'
            }).encode())
    
    def do_DELETE(self):
        """Remove label from an issue"""
        try:
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())
            
            repo = data.get('repo')
            issue = data.get('issue')
            label = data.get('label')
            
            if not repo or not issue or not label:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing required fields: repo, issue, label'
                }).encode())
                return
            
            # Remove label via GitHub API
            url = f'https://api.github.com/repos/{repo}/issues/{issue}/labels/{label}'
            self._make_github_request('DELETE', url)
            
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': f'Removed label "{label}" from issue #{issue}'
            }).encode())
            
        except requests.exceptions.HTTPError as e:
            self._set_headers(e.response.status_code)
            self.wfile.write(json.dumps({
                'error': f'GitHub API error: {str(e)}'
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': f'Server error: {str(e)}'
            }).encode())
