import csv
import pandas as pd
import json
import os
from datetime import datetime
from config import *
from github_persistence import GitHubPersistence

class StoreProcessor:
    def __init__(self, csv_file_path=CSV_FILE_PATH):
        self.csv_file_path = csv_file_path
        self.github_persistence = GitHubPersistence()
        self.sent_emails = self.load_sent_emails()
        
    def load_sent_emails(self):
        """Load list of emails that have already been sent to avoid duplicates"""
        sent_emails = set()
        try:
            # First try to load from GitHub (most up-to-date)
            github_data = self.github_persistence.load_from_github()
            
            # Load from local JSON file
            local_emails = set()
            json_file = "sent_emails.json"
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    local_emails = set(data.get('sent_emails', []))
                    print(f"✓ Loaded {len(local_emails)} sent emails from local JSON")
            
            # Merge GitHub and local data
            if github_data:
                github_emails = set(github_data.get('sent_emails', []))
                sent_emails = local_emails.union(github_emails)
                print(f"📊 Merged emails: Local={len(local_emails)}, GitHub={len(github_emails)}, Total={len(sent_emails)}")
            else:
                sent_emails = local_emails
                print(f"✓ Using local emails only: {len(sent_emails)}")
            
            # Fallback to log file if no JSON data
            if not sent_emails:
                try:
                    with open(SENT_EMAILS_LOG, 'r', encoding='utf-8') as f:
                        for line in f:
                            parts = line.strip().split(' | ')
                            if len(parts) >= 2:
                                sent_emails.add(parts[1])  # email address
                    print(f"✓ Loaded {len(sent_emails)} sent emails from log file")
                except FileNotFoundError:
                    print("✓ No sent emails found, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading sent emails: {e}")
        return sent_emails
    
    def save_sent_emails(self):
        """Save sent emails to both local JSON and GitHub for persistence"""
        try:
            # Prepare data
            data = {
                'sent_emails': list(self.sent_emails),
                'last_updated': datetime.now().isoformat()
            }
            
            # Save to local JSON file
            json_file = "sent_emails.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Save to GitHub for persistence across Render runs
            self.github_persistence.save_to_github(data)
            
        except Exception as e:
            print(f"⚠️ Error saving sent emails: {e}")
    
    def load_stores(self):
        """Load and filter stores from CSV file"""
        try:
            df = pd.read_csv(self.csv_file_path)
            print(f"✓ Loaded {len(df)} total stores from CSV")
            
            # Determine which email column to use
            email_col = 'cleaned_email' if 'cleaned_email' in df.columns else 'email'
            print(f"✓ Using email column: {email_col}")
            
            # Filter out stores that have already been emailed
            before_filter = len(df)
            df = df[~df[email_col].isin(self.sent_emails)]
            after_filter = len(df)
            print(f"✓ Filtered out {before_filter - after_filter} already-sent emails")
            
            # Filter out stores with invalid emails
            before_invalid = len(df)
            df = df[df[email_col].notna() & (df[email_col] != '')]
            after_invalid = len(df)
            print(f"✓ Filtered out {before_invalid - after_invalid} invalid emails")
            
            # Filter out stores with obvious invalid emails
            before_obvious = len(df)
            df = df[~df[email_col].str.contains('filler@godaddy.com', na=False)]
            df = df[~df[email_col].str.contains('example.com', na=False)]
            after_obvious = len(df)
            print(f"✓ Filtered out {before_obvious - after_obvious} obvious invalid emails")
            
            # If using original email column, clean up email addresses (remove extra text)
            if email_col == 'email':
                df[email_col] = df[email_col].str.extract(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
            
            # Remove rows where email is missing after processing
            before_final = len(df)
            df = df[df[email_col].notna()]
            after_final = len(df)
            print(f"✓ Final filtering: {before_final - after_final} emails removed")
            
            # Ensure there's always an 'email' column for the rest of the system
            if email_col == 'cleaned_email':
                df['email'] = df['cleaned_email']
            
            print(f"✓ Final result: {len(df)} stores ready for emailing")
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Error loading stores: {e}")
            return []
    
    def get_stores_for_emailing(self, limit=DAILY_EMAIL_LIMIT):
        """Get stores ready for emailing, prioritizing by certain criteria"""
        stores = self.load_stores()
        
        if not stores:
            return []
        
        # Sort stores by priority (you can customize this logic)
        # For now, we'll prioritize stores that are flagged as true
        stores.sort(key=lambda x: (x.get('flagged', '') != 'true', x.get('name', '')))
        
        # Return the specified number of stores
        return stores[:limit]
    
    def get_email_template(self, store_type):
        """Get the appropriate email template for the store type"""
        return EMAIL_TEMPLATES.get(store_type, DEFAULT_TEMPLATE)
    
    def format_email(self, store_data):
        """Format email content for a specific store"""
        store_name = store_data.get('name', 'Store Owner')
        store_type = store_data.get('query', '')
        
        template_data = self.get_email_template(store_type)
        subject = template_data['subject']
        template = template_data['template']
        
        # Format the email body
        formatted_body = template.format(store_name=store_name)
        
        return {
            'to_email': store_data.get('email'),
            'subject': subject,
            'body': formatted_body,
            'store_name': store_name,
            'store_type': store_type
        }
    
    def mark_email_sent(self, email):
        """Mark an email as sent to avoid duplicates"""
        self.sent_emails.add(email)
        self.save_sent_emails()  # Save immediately after marking
    
    def get_stats(self):
        """Get statistics about the email campaign"""
        try:
            df = pd.read_csv(self.csv_file_path)
            total_stores = len(df)
            stores_with_emails = len(df[df['email'].notna() & (df['email'] != '')])
            already_sent = len(self.sent_emails)
            remaining = stores_with_emails - already_sent
            
            return {
                'total_stores': total_stores,
                'stores_with_emails': stores_with_emails,
                'already_sent': already_sent,
                'remaining': remaining
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {} 