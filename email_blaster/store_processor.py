import csv
import pandas as pd
from datetime import datetime
from config import *

class StoreProcessor:
    def __init__(self, csv_file_path=CSV_FILE_PATH):
        self.csv_file_path = csv_file_path
        self.sent_emails = self.load_sent_emails()
        
    def load_sent_emails(self):
        """Load list of emails that have already been sent to avoid duplicates"""
        sent_emails = set()
        try:
            with open(SENT_EMAILS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(' | ')
                    if len(parts) >= 2:
                        sent_emails.add(parts[1])  # email address
        except FileNotFoundError:
            pass
        return sent_emails
    
    def load_stores(self):
        """Load and filter stores from CSV file"""
        try:
            df = pd.read_csv(self.csv_file_path)
            
            # Determine which email column to use
            email_col = 'cleaned_email' if 'cleaned_email' in df.columns else 'email'
            
            # Filter out stores that have already been emailed
            df = df[~df[email_col].isin(self.sent_emails)]
            
            # Filter out stores with invalid emails
            df = df[df[email_col].notna() & (df[email_col] != '')]
            
            # Filter out stores with obvious invalid emails
            df = df[~df[email_col].str.contains('filler@godaddy.com', na=False)]
            df = df[~df[email_col].str.contains('example.com', na=False)]
            
            # If using original email column, clean up email addresses (remove extra text)
            if email_col == 'email':
                df[email_col] = df[email_col].str.extract(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
            
            # Remove rows where email is missing after processing
            df = df[df[email_col].notna()]
            
            # Ensure there's always an 'email' column for the rest of the system
            if email_col == 'cleaned_email':
                df['email'] = df['cleaned_email']
            
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