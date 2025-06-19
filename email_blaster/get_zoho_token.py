#!/usr/bin/env python3
"""
Zoho OAuth Token Generator
Handles the OAuth 2.0 flow to get a refresh token for Zoho Mail API
"""

import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse

def get_authorization_url(client_id, redirect_uri="http://localhost"):
    """Generate the authorization URL for Zoho OAuth"""
    base_url = "https://accounts.zoho.com/oauth/v2/auth"
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': 'ZohoMail.messages.CREATE offline_access',
        'redirect_uri': redirect_uri,
        'access_type': 'offline'
    }
    
    auth_url = f"{base_url}?{urlencode(params)}"
    return auth_url

def exchange_code_for_tokens(client_id, client_secret, auth_code, redirect_uri="http://localhost"):
    """Exchange authorization code for access and refresh tokens"""
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error exchanging code for tokens: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def main():
    """Main function to get Zoho refresh token"""
    print("Zoho OAuth Token Generator")
    print("=" * 50)
    
    # Get client credentials
    client_id = input("Enter your Zoho Client ID: ").strip()
    client_secret = input("Enter your Zoho Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required!")
        return
    
    # Generate authorization URL
    auth_url = get_authorization_url(client_id)
    
    print("\n📋 Step 1: Authorize your application")
    print("Opening browser for authorization...")
    
    # Open browser for authorization
    webbrowser.open(auth_url)
    
    print("\n📝 After authorizing in the browser:")
    print("1. You'll be redirected to a URL like: http://localhost?code=XXXXX")
    print("2. Copy the 'code' parameter from that URL")
    print("3. Paste it below")
    
    # Get authorization code from user
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ Authorization code is required!")
        return
    
    print("\n🔄 Step 2: Exchanging code for tokens...")
    
    # Exchange code for tokens
    token_data = exchange_code_for_tokens(client_id, client_secret, auth_code)
    
    if token_data and 'refresh_token' in token_data:
        print("\n✅ Success! Here are your tokens:")
        print(f"Refresh Token: {token_data['refresh_token']}")
        print(f"Access Token: {token_data.get('access_token', 'N/A')}")
        print(f"Expires In: {token_data.get('expires_in', 'N/A')} seconds")
        
        print("\n📝 Add this to your .env file:")
        print(f"ZOHO_REFRESH_TOKEN={token_data['refresh_token']}")
        
    else:
        print("\n❌ Failed to get tokens!")
        if token_data:
            print(f"Error: {token_data}")

if __name__ == "__main__":
    main() 