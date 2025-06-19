#!/usr/bin/env python3
"""
Test script for Email Blaster system
Tests all components without sending actual emails
"""

import sys
from pathlib import Path

# Import all modules at the top level
try:
    from config import *
    from store_processor import StoreProcessor
    from zoho_mailer import ZohoMailer
    from email_blaster import EmailBlaster
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    if IMPORTS_OK:
        print("✓ All modules imported successfully")
        return True
    else:
        print(f"✗ Import failed: {IMPORT_ERROR}")
        return False

def test_csv_loading():
    """Test CSV file loading"""
    print("\nTesting CSV file loading...")
    
    try:
        processor = StoreProcessor()
        stores = processor.load_stores()
        
        if stores:
            print(f"✓ Successfully loaded {len(stores)} stores from CSV")
            
            # Show sample data
            sample = stores[0]
            print(f"  Sample store: {sample.get('name', 'Unknown')}")
            print(f"  Email: {sample.get('email', 'No email')}")
            print(f"  Type: {sample.get('query', 'Unknown')}")
            
            return True
        else:
            print("✗ No stores loaded from CSV")
            return False
            
    except Exception as e:
        print(f"✗ CSV loading failed: {e}")
        return False

def test_email_templates():
    """Test email template generation"""
    print("\nTesting email templates...")
    
    try:
        processor = StoreProcessor()
        
        # Test with sample store data
        sample_store = {
            'name': 'Test Store',
            'email': 'test@example.com',
            'query': 'tabletop game store'
        }
        
        email_data = processor.format_email(sample_store)
        
        print("✓ Email template generated successfully")
        print(f"  Subject: {email_data['subject']}")
        print(f"  To: {email_data['to_email']}")
        print(f"  Body preview: {email_data['body'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Email template generation failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        print(f"✓ Daily email limit: {DAILY_EMAIL_LIMIT}")
        print(f"✓ Email subject prefix: {EMAIL_SUBJECT_PREFIX}")
        print(f"✓ CSV file path: {CSV_FILE_PATH}")
        print(f"✓ Number of email templates: {len(EMAIL_TEMPLATES)}")
        
        # Check if Zoho credentials are set (but don't validate them)
        has_client_id = bool(ZOHO_CLIENT_ID)
        has_client_secret = bool(ZOHO_CLIENT_SECRET)
        has_refresh_token = bool(ZOHO_REFRESH_TOKEN)
        has_email = bool(ZOHO_EMAIL)
        
        print(f"✓ ZOHO_CLIENT_ID: {'Set' if has_client_id else 'Not set'}")
        print(f"✓ ZOHO_CLIENT_SECRET: {'Set' if has_client_secret else 'Not set'}")
        print(f"✓ ZOHO_REFRESH_TOKEN: {'Set' if has_refresh_token else 'Not set'}")
        print(f"✓ ZOHO_EMAIL: {'Set' if has_email else 'Not set'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Email Blaster System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_csv_loading,
        test_email_templates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Configure your Zoho API credentials in .env file")
        print("2. Test with: python email_blaster.py test")
        print("3. Preview emails: python email_blaster.py preview 1")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 