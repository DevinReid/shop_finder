#!/usr/bin/env python3
"""
Setup script for Email Blaster environment variables
Helps configure Zoho API credentials
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with Zoho API configuration"""
    env_content = """# Zoho Mail API Configuration
# Get these from your Zoho Developer Console: https://api-console.zoho.com/
ZOHO_CLIENT_ID=your_client_id_here
ZOHO_CLIENT_SECRET=your_client_secret_here
ZOHO_REFRESH_TOKEN=your_refresh_token_here
ZOHO_EMAIL=your_zoho_email@yourdomain.com

# Optional: Override default settings
# DAILY_EMAIL_LIMIT=5
# EMAIL_SUBJECT_PREFIX="Wholesale Partnership Inquiry - "
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created!")
    print("\n📝 Next steps:")
    print("1. Go to https://api-console.zoho.com/")
    print("2. Create a new client for Zoho Mail API")
    print("3. Get your Client ID, Client Secret, and Refresh Token")
    print("4. Update the .env file with your actual credentials")
    print("5. Test the setup with: python email_blaster.py test")

def check_env_setup():
    """Check if environment variables are properly configured"""
    required_vars = [
        'ZOHO_CLIENT_ID',
        'ZOHO_CLIENT_SECRET', 
        'ZOHO_REFRESH_TOKEN',
        'ZOHO_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nRun 'python setup_env.py' to create .env file")
        return False
    else:
        print("✅ All environment variables are configured!")
        return True

def main():
    """Main setup function"""
    print("Email Blaster Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("No .env file found. Creating one...")
        create_env_file()
    else:
        print("Found existing .env file")
        check_env_setup()

if __name__ == "__main__":
    main() 