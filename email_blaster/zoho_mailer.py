import requests
import json
import time
from datetime import datetime
from config import *

class ZohoMailer:
    def __init__(self):
        self.client_id = ZOHO_CLIENT_ID
        self.client_secret = ZOHO_CLIENT_SECRET
        self.refresh_token = ZOHO_REFRESH_TOKEN
        self.email = ZOHO_EMAIL
        self.access_token = None
        self.token_expiry = None
        
    def get_access_token(self):
        """Get or refresh access token for Zoho API"""
        if self.access_token and self.token_expiry and time.time() < self.token_expiry:
            return self.access_token
            
        url = "https://accounts.zoho.com/oauth/v2/token"
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()
            if 'access_token' not in token_data:
                print(f"Error: 'access_token' not in response: {token_data}")
                return None
            self.access_token = token_data['access_token']
            self.token_expiry = time.time() + token_data['expires_in'] - 300  # 5 min buffer
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def send_email(self, to_email, subject, body, store_name=None):
        """Send email using Zoho Mail API"""
        access_token = self.get_access_token()
        if not access_token:
            return False, "Failed to get access token"
        
        # Get the user's accountId (same logic as test_connection)
        accounts_url = "https://mail.zoho.com/api/accounts"
        headers = {
            'Authorization': f'Zoho-oauthtoken {access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(accounts_url, headers=headers)
            response.raise_for_status()
            accounts_data = response.json()
            account_id = None
            if 'data' in accounts_data:
                for acc in accounts_data['data']:
                    if acc.get('primaryEmailAddress', '').lower() == self.email.lower():
                        account_id = acc.get('accountId')
                        break
                if not account_id and accounts_data['data']:
                    account_id = accounts_data['data'][0].get('accountId')
            if not account_id:
                return False, "Could not find accountId for the configured email."
        except requests.exceptions.RequestException as e:
            return False, f"Failed to fetch accounts: {e}"

        url = f"https://mail.zoho.com/api/accounts/{account_id}/messages"
        
        # Prepare email data
        email_data = {
            "fromAddress": self.email,
            "toAddress": to_email,
            "subject": subject,
            "content": body,
            "mailFormat": "html"
        }
        try:
            response = requests.post(url, headers=headers, json=email_data)
            response.raise_for_status()
            # Log successful email
            self.log_email(to_email, subject, store_name, "SUCCESS")
            return True, "Email sent successfully"
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to send email: {e}"
            self.log_email(to_email, subject, store_name, f"FAILED: {error_msg}")
            return False, error_msg
    
    def log_email(self, to_email, subject, store_name, status):
        """Log email sending attempts"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | {to_email} | {store_name} | {subject} | {status}\n"
        
        if "SUCCESS" in status:
            with open(SENT_EMAILS_LOG, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        else:
            with open(FAILED_EMAILS_LOG, 'a', encoding='utf-8') as f:
                f.write(log_entry)
    
    def test_connection(self):
        """Test the Zoho API connection"""
        access_token = self.get_access_token()
        if not access_token:
            return False, "Failed to get access token"
        
        # Step 1: Get the user's accountId
        accounts_url = "https://mail.zoho.com/api/accounts"
        headers = {
            'Authorization': f'Zoho-oauthtoken {access_token}'
        }
        try:
            response = requests.get(accounts_url, headers=headers)
            response.raise_for_status()
            accounts_data = response.json()
            # Find the accountId for the primary email
            account_id = None
            if 'data' in accounts_data:
                for acc in accounts_data['data']:
                    if acc.get('primaryEmailAddress', '').lower() == self.email.lower():
                        account_id = acc.get('accountId')
                        break
                if not account_id and accounts_data['data']:
                    # Fallback: use the first accountId
                    account_id = accounts_data['data'][0].get('accountId')
            if not account_id:
                return False, "Could not find accountId for the configured email."
        except requests.exceptions.RequestException as e:
            return False, f"Failed to fetch accounts: {e}"

        # Step 2: Test the account details endpoint
        url = f"https://mail.zoho.com/api/accounts/{account_id}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return True, "Connection successful"
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {e}" 