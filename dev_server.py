#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Development Server
Simple HTTP server with auto-reload for dashboard development
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with better MIME types and CORS"""
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Colorful logging
        print(f"🌐 {self.address_string()} - {format % args}")


def main():
    """Start local development server"""
    
    # Configuration
    PORT = int(os.getenv('PORT', 8000))
    DIRECTORY = 'docs'
    
    # Change to docs directory
    os.chdir(DIRECTORY)
    
    # Create server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print("\n" + "="*60)
        print("🚀 GitHub Repository Analytics Dashboard - Dev Server")
        print("="*60)
        print(f"\n📂 Serving directory: {Path(DIRECTORY).absolute()}")
        print(f"🌐 Server running at: http://localhost:{PORT}")
        print(f"📊 Dashboard URL: http://localhost:{PORT}/index.html")
        print("\n💡 Tips:")
        print("   • Press Ctrl+C to stop the server")
        print("   • Edit files and refresh browser to see changes")
        print("   • Run 'python stats.py' to update data")
        print("   • Run 'python generate_badges.py' to update badges")
        print("\n" + "="*60 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n⚠️  Server stopped by user")
            print("👋 Goodbye!\n")
            sys.exit(0)


if __name__ == '__main__':
    main()
