#!/usr/bin/env python3
"""
Email Blaster - Automated wholesale outreach system
Sends personalized emails to potential wholesale clients based on store type
"""

import time
import sys
from zoho_mailer import ZohoMailer
from store_processor import StoreProcessor
from config import DAILY_EMAIL_LIMIT

class EmailBlaster:
    def __init__(self):
        self.mailer = ZohoMailer()
        self.processor = StoreProcessor()
        
    def test_setup(self):
        """Test the email system setup"""
        print("Testing Email Blaster Setup...")
        print("=" * 50)
        
        # Test Zoho connection
        print("1. Testing Zoho API connection...")
        success, message = self.mailer.test_connection()
        print(f"   Result: {'✓' if success else '✗'} {message}")
        
        # Test store data loading
        print("2. Testing store data loading...")
        stores = self.processor.load_stores()
        print(f"   Result: {'✓' if stores else '✗'} Found {len(stores)} stores with valid emails")
        
        # Show stats
        print("3. Campaign Statistics:")
        stats = self.processor.get_stats()
        for key, value in stats.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        return success and stores
    
    def send_daily_emails(self, limit=None):
        """Send the daily batch of emails"""
        if limit is None:
            limit = DAILY_EMAIL_LIMIT
            
        print(f"Sending {limit} emails...")
        print("=" * 50)
        
        # Get stores to email
        stores = self.processor.get_stores_for_emailing(limit)
        
        if not stores:
            print("No stores available for emailing!")
            return
        
        print(f"Found {len(stores)} stores to email")
        
        success_count = 0
        failed_count = 0
        
        for i, store in enumerate(stores, 1):
            print(f"\n{i}/{len(stores)}: Processing {store.get('name', 'Unknown Store')}")
            
            # Format email
            email_data = self.processor.format_email(store)
            
            if not email_data['to_email']:
                print("   ✗ No valid email address")
                failed_count += 1
                continue
            
            # Send email
            success, message = self.mailer.send_email(
                email_data['to_email'],
                email_data['subject'],
                email_data['body'],
                email_data['store_name']
            )
            
            if success:
                print(f"   ✓ Email sent to {email_data['to_email']}")
                self.processor.mark_email_sent(email_data['to_email'])
                success_count += 1
            else:
                print(f"   ✗ Failed: {message}")
                failed_count += 1
            
            # Add delay between emails to avoid rate limiting
            if i < len(stores):
                print("   Waiting 2 seconds before next email...")
                time.sleep(2)
        
        print("\n" + "=" * 50)
        print("Email Campaign Complete!")
        print(f"Successfully sent: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"Total processed: {len(stores)}")
    
    def preview_emails(self, limit=3):
        """Preview emails without sending them"""
        print(f"Previewing {limit} emails (not sending)...")
        print("=" * 50)
        
        stores = self.processor.get_stores_for_emailing(limit)
        
        if not stores:
            print("No stores available for preview!")
            return
        
        for i, store in enumerate(stores, 1):
            print(f"\n{i}. Store: {store.get('name', 'Unknown')}")
            print(f"   Type: {store.get('query', 'Unknown')}")
            print(f"   Email: {store.get('email', 'No email')}")
            
            email_data = self.processor.format_email(store)
            print(f"   Subject: {email_data['subject']}")
            print(f"   Body Preview: {email_data['body'][:100]}...")
            print("-" * 30)
    
    def run_interactive(self):
        """Run the email blaster in interactive mode"""
        print("Email Blaster - Interactive Mode")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Test setup")
            print("2. Preview emails (3 stores)")
            print("3. Send daily emails")
            print("4. Send custom number of emails")
            print("5. Show statistics")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.test_setup()
            elif choice == '2':
                self.preview_emails()
            elif choice == '3':
                self.send_daily_emails()
            elif choice == '4':
                try:
                    count = int(input("How many emails to send? "))
                    self.send_daily_emails(count)
                except ValueError:
                    print("Please enter a valid number")
            elif choice == '5':
                stats = self.processor.get_stats()
                print("\nCampaign Statistics:")
                for key, value in stats.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def send_test_email(self, to_email):
        """Send a test email to a specified address"""
        subject = "Test Email from Email Blaster"
        body = "<p>This is a test email sent from the Email Blaster system. If you received this, your Zoho Mail API is working!<br><br>Best,<br>Email Blaster</p>"
        print(f"Sending test email to {to_email}...")
        success, message = self.mailer.send_email(to_email, subject, body, store_name="Test Recipient")
        if success:
            print(f"✓ Test email sent to {to_email}")
        else:
            print(f"✗ Failed to send test email: {message}")

def main():
    """Main function"""
    blaster = EmailBlaster()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            blaster.test_setup()
        elif command == 'preview':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            blaster.preview_emails(limit)
        elif command == 'send':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            blaster.send_daily_emails(limit)
        elif command == 'stats':
            stats = blaster.processor.get_stats()
            print("Campaign Statistics:")
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        elif command == 'send_test':
            if len(sys.argv) > 2:
                to_email = sys.argv[2]
                blaster.send_test_email(to_email)
            else:
                print("Usage: python email_blaster.py send_test your@email.com")
        else:
            print("Usage: python email_blaster.py [test|preview|send|stats|send_test] [limit|email]")
            print("Or run without arguments for interactive mode")
    else:
        blaster.run_interactive()

if __name__ == "__main__":
    main() 