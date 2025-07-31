#!/usr/bin/env python3
"""
Email Cleaner - OpenAI-powered email address cleaning for scraped data
Cleans up email addresses from website scraping while preserving all data fields
"""

import csv
from openai import OpenAI
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
INPUT_CSV = "C:/Users/Dreid/Desktop/Brain/Projects/shop_finder/fenclaw_search/stores_with_emails.csv"  # Your main stores file
OUTPUT_CSV = "cleaned_stores_with_emails.csv"  # Output in email_blaster directory
BATCH_SIZE = 30  # Smaller batches for better accuracy
SLEEP_TIME = 2  # seconds between API calls to avoid rate limits

def load_rows():
    """Load all rows from the input CSV file"""
    try:
        with open(INPUT_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"✓ Loaded {len(rows)} rows from {INPUT_CSV}")
            return rows
    except FileNotFoundError:
        print(f"❌ Input file not found: {INPUT_CSV}")
        print("Please check the file path and try again.")
        return []
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return []

def chunk_rows(rows, size):
    """Split rows into chunks for batch processing"""
    for i in range(0, len(rows), size):
        yield rows[i:i + size]

def format_prompt(batch):
    """Create a prompt for OpenAI to clean email addresses"""
    prompt = """Clean and extract valid email addresses from the following scraped data. 
For each row, return only the best/most valid email address found, or 'INVALID' if no valid email exists.
Format: store_name: cleaned_email

Rules:
- Extract only real, valid email addresses
- Remove any extra text, URLs, or formatting
- If multiple emails exist, choose the best business email
- If no valid email, return 'INVALID'
- Remove emails like 'noreply@', 'info@example.com', or obvious placeholder emails

Data to clean:
"""
    
    for i, row in enumerate(batch):
        store_name = row.get('name', f'Store_{i}')
        email = row.get('email', '')
        prompt += f"- {store_name}: {email}\n"
    
    return prompt

def call_openai(prompt):
    """Call OpenAI API to clean email addresses"""
    try:
        response = client.chat.completions.create(
            model='gpt-4',  # Use gpt-4 for better accuracy
            messages=[
                {"role": "system", "content": "You are an expert at cleaning and validating email addresses from scraped website data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return None

def parse_cleaned_output(output_text, original_batch):
    """Parse OpenAI response and map cleaned emails back to store names"""
    cleaned = {}
    
    if not output_text:
        # Fallback: return original emails
        for row in original_batch:
            cleaned[row.get('name', '')] = row.get('email', '')
        return cleaned
    
    lines = output_text.strip().splitlines()
    for line in lines:
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                name = parts[0].strip(' -•')
                email = parts[1].strip()
                
                # Filter out invalid responses
                if email.lower() not in ['invalid', 'none', 'n/a', '']:
                    cleaned[name] = email
                else:
                    cleaned[name] = ''  # Mark as empty if invalid
    
    # Fallback for any missing stores
    for row in original_batch:
        store_name = row.get('name', '')
        if store_name not in cleaned:
            cleaned[store_name] = row.get('email', '')  # Use original as fallback
    
    return cleaned

def main():
    """Main function to process email cleaning"""
    print("Email Cleaner - Starting...")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Load data
    rows = load_rows()
    if not rows:
        return
    
    # Show sample of what we're processing
    print("\nSample data (first 3 rows):")
    for i, row in enumerate(rows[:3]):
        print(f"  {i+1}. {row.get('name', 'Unknown')}: {row.get('email', 'No email')}")
    
    # Confirm before proceeding
    proceed = input(f"\nProcess {len(rows)} rows for email cleaning? (y/N): ").strip().lower()
    if proceed != 'y':
        print("Operation cancelled.")
        return
    
    cleaned_data = []
    total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\nProcessing {len(rows)} rows in {total_batches} batches...")
    
    for batch_num, batch in enumerate(chunk_rows(rows, BATCH_SIZE), 1):
        print(f"Processing batch {batch_num}/{total_batches}...")
        
        # Create prompt and call OpenAI
        prompt = format_prompt(batch)
        output = call_openai(prompt)
        
        # Parse results
        if output:
            parsed = parse_cleaned_output(output, batch)
        else:
            # Fallback: use original emails
            parsed = {row.get('name', ''): row.get('email', '') for row in batch}
        
        # Add cleaned emails to rows
        for row in batch:
            store_name = row.get('name', '')
            row['cleaned_email'] = parsed.get(store_name, row.get('email', ''))
            cleaned_data.append(row)
        
        # Sleep to avoid rate limiting
        if batch_num < total_batches:
            print(f"  Waiting {SLEEP_TIME} seconds...")
            time.sleep(SLEEP_TIME)
    
    # Write results
    try:
        fieldnames = list(cleaned_data[0].keys())
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_data)
        
        print(f"\n✅ Success! Cleaned data saved to: {OUTPUT_CSV}")
        
        # Show summary
        valid_emails = sum(1 for row in cleaned_data if row.get('cleaned_email', '').strip())
        print("📊 Summary:")
        print(f"   Total stores processed: {len(cleaned_data)}")
        print(f"   Valid emails found: {valid_emails}")
        print(f"   Success rate: {valid_emails/len(cleaned_data)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Error writing output file: {e}")

if __name__ == '__main__':
    main() 