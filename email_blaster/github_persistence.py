#!/usr/bin/env python3
"""
GitHub Persistence - Save sent emails tracking to GitHub
This allows the JSON file to persist between Render cron job runs
"""

import json
import os
import base64
import requests
from datetime import datetime

class GitHubPersistence:
    def __init__(self, repo_owner="DevinReid", repo_name="shop_finder", 
                 file_path="email_blaster/sent_emails.json", branch="main"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.file_path = file_path
        self.branch = branch
        self.github_token = os.getenv('GITHUB_TOKEN')
        
    def get_file_sha(self):
        """Get the current SHA of the file on GitHub"""
        if not self.github_token:
            return None
            
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.file_path}"
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()['sha']
            return None
        except Exception as e:
            print(f"Error getting file SHA: {e}")
            return None
    
    def merge_sent_emails(self, local_emails, github_data):
        """Merge local and GitHub sent emails, avoiding duplicates"""
        if not github_data:
            return local_emails
            
        github_emails = set(github_data.get('sent_emails', []))
        merged_emails = local_emails.union(github_emails)
        
        print(f"📊 Merging emails: Local={len(local_emails)}, GitHub={len(github_emails)}, Merged={len(merged_emails)}")
        return merged_emails
    
    def save_to_github(self, data):
        """Save the sent emails data to GitHub with merging"""
        if not self.github_token:
            print("⚠️ GITHUB_TOKEN not set, skipping GitHub save")
            return False
            
        # First, load existing data from GitHub
        existing_data = self.load_from_github()
        
        # Merge the sent emails
        if existing_data:
            local_emails = set(data.get('sent_emails', []))
            merged_emails = self.merge_sent_emails(local_emails, existing_data)
            data['sent_emails'] = list(merged_emails)
        
        # Prepare the file content
        file_content = json.dumps(data, indent=2)
        encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        
        # Get current SHA
        sha = self.get_file_sha()
        
        # Prepare the request
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.file_path}"
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        payload = {
            'message': f'Update sent emails tracking - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': encoded_content,
            'branch': self.branch
        }
        
        if sha:
            payload['sha'] = sha
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                print(f"✅ Successfully saved {len(data.get('sent_emails', []))} sent emails to GitHub")
                return True
            else:
                print(f"❌ Failed to save to GitHub: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error saving to GitHub: {e}")
            return False
    
    def load_from_github(self):
        """Load the sent emails data from GitHub"""
        if not self.github_token:
            print("⚠️ GITHUB_TOKEN not set, using local file only")
            return None
            
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.file_path}"
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                content = response.json()['content']
                decoded_content = base64.b64decode(content).decode('utf-8')
                data = json.loads(decoded_content)
                print(f"✅ Loaded {len(data.get('sent_emails', []))} sent emails from GitHub")
                return data
            else:
                print(f"⚠️ Could not load from GitHub: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ Error loading from GitHub: {e}")
            return None 