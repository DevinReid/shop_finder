#!/usr/bin/env python3
"""
Cron job setup for Email Blaster
Helps configure automated daily email sending
"""

import os
import platform
from pathlib import Path

def get_python_path():
    """Get the current Python executable path"""
    return os.sys.executable

def get_script_path():
    """Get the absolute path to the email_blaster.py script"""
    return str(Path(__file__).parent / 'email_blaster.py')

def create_cron_command():
    """Create the cron command for daily email sending"""
    python_path = get_python_path()
    script_path = get_script_path()
    
    # Change to the script directory and run the email blaster
    cron_command = f"cd {Path(script_path).parent} && {python_path} email_blaster.py send"
    
    return cron_command

def setup_windows_task():
    """Setup Windows Task Scheduler task"""
    print("Setting up Windows Task Scheduler...")
    
    python_path = get_python_path()
    script_path = get_script_path()
    script_dir = Path(script_path).parent
    
    # Create batch file
    batch_content = f"""@echo off
cd /d "{script_dir}"
"{python_path}" email_blaster.py send
"""
    
    batch_file = script_dir / "run_email_blaster.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"✅ Created batch file: {batch_file}")
    print("\n📝 To set up Windows Task Scheduler:")
    print("1. Open Task Scheduler (taskschd.msc)")
    print("2. Create Basic Task")
    print("3. Name: 'Email Blaster Daily'")
    print("4. Trigger: Daily at 9:00 AM")
    print(f"5. Action: Start program: {batch_file}")
    print("6. Finish")

def setup_linux_cron():
    """Setup Linux/Mac cron job"""
    print("Setting up Linux/Mac cron job...")
    
    cron_command = create_cron_command()
    
    print("📝 To add to crontab, run:")
    print("crontab -e")
    print("\nThen add this line to send emails daily at 9:00 AM:")
    print(f"0 9 * * * {cron_command}")
    print("\nOr to send emails every weekday at 9:00 AM:")
    print(f"0 9 * * 1-5 {cron_command}")

def show_manual_setup():
    """Show manual setup instructions"""
    print("Manual Setup Instructions")
    print("=" * 50)
    
    cron_command = create_cron_command()
    
    print("Cron Command:")
    print(cron_command)
    print("\nCommon cron schedules:")
    print("Daily at 9:00 AM:    0 9 * * *")
    print("Weekdays at 9:00 AM: 0 9 * * 1-5")
    print("Every 2 hours:       0 */2 * * *")
    print("Every Monday:        0 9 * * 1")

def main():
    """Main setup function"""
    print("Email Blaster - Cron Setup")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Detected Windows system")
        setup_windows_task()
    elif system in ["linux", "darwin"]:
        print("Detected Linux/Mac system")
        setup_linux_cron()
    else:
        print("Unknown system, showing manual setup...")
        show_manual_setup()
    
    print("\n" + "=" * 50)
    print("Additional Notes:")
    print("- Make sure your .env file is configured with Zoho credentials")
    print("- Test the setup first with: python email_blaster.py test")
    print("- Monitor logs in sent_emails.log and failed_emails.log")
    print("- The system will automatically avoid sending duplicate emails")

if __name__ == "__main__":
    main() 