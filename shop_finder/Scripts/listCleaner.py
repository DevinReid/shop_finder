import csv
import re
import os
from shop_finder.config import FILES


# Known TLDs for email boundary
TLDs = "com|net|org|edu|io|co|us|biz|store|shop|info"

# Common prefixes that might indicate a placeholder or system email
SUSPICIOUS_PREFIXES = [
    'service', 'contact', 'info', 'help', 'usemail', 'support', 'team', 'admin'
]

# File paths
MASTER_FILE = FILES["master_list"]
WITH_EMAILS_FILE = FILES["with_emails"]
WITHOUT_EMAILS_FILE = FILES["without_emails"]
CLEAN_WITH_EMAILS_FILE = "fenclaw_search/clean_with_emails.csv"
CLEAN_WITHOUT_EMAILS_FILE = "fenclaw_search/clean_without_emails.csv"

def load_excluded_retailers():
    """Load the list of retailers to exclude"""
    excluded_retailers = set()
    try:
        with open(FILES["excluded_retailers"], newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                excluded_retailers.add(row["retailer_name"].strip().lower())
    except FileNotFoundError:
        print("⚠️ Warning: excluded_retailers.csv not found. No retailers will be excluded.")
    return excluded_retailers

def is_excluded_retailer(name, excluded_retailers):
    """Check if a store name matches any excluded retailer"""
    name_lower = name.strip().lower()
    return any(excluded.lower() in name_lower for excluded in excluded_retailers)

def clean_smart_emails(text):
    emails = re.findall(rf'\b[\w\.-]+@[\w\.-]+\.(?:{TLDs})\b', text, re.IGNORECASE)
    emails = list(set(emails))
    flagged = []
    for email in emails:
        local_part = email.split("@")[0].lower()
        flagged.append((email, any(prefix in local_part for prefix in SUSPICIOUS_PREFIXES)))
    return flagged

def load_csv(file_path):
    if not os.path.exists(file_path):
        return [], []
    with open(file_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def save_csv(file_path, rows, fieldnames):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def is_duplicate(entry, existing_entries):
    for other in existing_entries:
        if (
            entry.get("name", "").strip().lower() == other.get("name", "").strip().lower() and
            entry.get("address", "").strip().lower() == other.get("address", "").strip().lower() and
            entry.get("city", "").strip().lower() == other.get("city", "").strip().lower()
        ):
            return True
    return False

def create_clean_retailer_files(with_emails, without_emails):
    """Create clean versions of the retailer files with excluded retailers removed"""
    # Load excluded retailers
    excluded_retailers = load_excluded_retailers()
    print(f"\n📋 Loaded {len(excluded_retailers)} excluded retailers")
    
    # Fields to remove from output
    fields_to_remove = ["coordinates", "location_id"]
    
    # Process each file
    files_to_process = [
        (with_emails, CLEAN_WITH_EMAILS_FILE),
        (without_emails, CLEAN_WITHOUT_EMAILS_FILE)
    ]
    
    total_removed = 0
    
    for entries, output_file in files_to_process:
        kept_entries = []
        removed_count = 0

        # Only do this if entries exist!
        if entries:
            # Determine fieldnames
            fieldnames = [field for field in entries[0].keys() if field not in fields_to_remove]

            # Process each entry
            for row in entries:
                if is_excluded_retailer(row["name"], excluded_retailers):
                    removed_count += 1
                    continue

                # Create new row without unwanted fields
                clean_row = {field: row[field] for field in fieldnames}
                kept_entries.append(clean_row)

            # Sort entries by city
            kept_entries.sort(key=lambda x: x["city"].lower())

            # Write output file
            save_csv(output_file, kept_entries, fieldnames)

            # Count entries per city
            city_counts = {}
            for entry in kept_entries:
                city = entry["city"]
                city_counts[city] = city_counts.get(city, 0) + 1

            print(f"\n📊 Results for {output_file}:")
            print(f"   - Removed {removed_count} excluded retailers")
            print(f"   - Kept {len(kept_entries)} entries")
            print(f"   - Removed fields: {', '.join(fields_to_remove)}")
            print("\n   📍 Entries per city:")
            for city, count in sorted(city_counts.items()):
                print(f"      - {city}: {count}")

            total_removed += removed_count

        else:
            print(f"⚠️ No data rows in {output_file}. Skipping processing.")


def process_master_list():
    master_data, master_fields = load_csv(MASTER_FILE)
    with_emails, _ = load_csv(WITH_EMAILS_FILE)
    without_emails, _ = load_csv(WITHOUT_EMAILS_FILE)
    master_data = dedupe(master_data)

    print(f"📥 Loaded {len(master_data)} entries from master_list.csv")

    updated_master = []
    updated_with_emails = with_emails[:]
    updated_without_emails = without_emails[:]

    moved_to_with = 0
    moved_to_without = 0
    newly_flagged = 0

    for row in master_data:
        # Ensure all fields have at least empty string values
        for field in master_fields:
            if field not in row or row[field] is None:
                row[field] = ""

        row["sorted"] = "true"
        email = row.get("email", "").strip()

        if email:
            result = clean_smart_emails(email)
            if result:
                email_cleaned, flagged = result[0]
                row["email"] = email_cleaned

                if flagged:
                    row["flagged"] = "true"
                    newly_flagged += 1
                else:
                    row.pop("flagged", "")  # Remove the key if it exists
            else:
                row.pop("flagged", "")

            if not is_duplicate(row, updated_with_emails):
                updated_with_emails.append(row)
                moved_to_with += 1
            else:
                # Silently skip duplicates
                pass
        else:
            if not is_duplicate(row, updated_without_emails):
                updated_without_emails.append(row)
                moved_to_without += 1
            else:
                # Silently skip duplicates
                pass

        updated_master.append(row)

    # Ensure all fieldnames are preserved (original + added ones)
    # Manually define desired column order
    fieldnames = [
        "sorted", "query", "city", "location_id", "coordinates", "name", "address", "website", "email", "flagged"
    ]

    # Save everything
    save_csv(MASTER_FILE, updated_master, fieldnames)
    save_csv(WITH_EMAILS_FILE, updated_with_emails, fieldnames)
    save_csv(WITHOUT_EMAILS_FILE, updated_without_emails, fieldnames)

    # ✅ Debug summary
    print(f"📤 Moved {moved_to_with} entries to stores_with_emails.csv")
    print(f"📤 Moved {moved_to_without} entries to stores_without_email.csv")
    print(f"🚩 Flagged {newly_flagged} suspicious email(s)")
    print("✅ Processing complete. All sorted entries marked.")
    
    # Create clean versions of the files
    print("\n🧹 Creating clean versions of files (excluding major retailers)...")
    create_clean_retailer_files(updated_with_emails, updated_without_emails)

def dedupe(rows):
    seen = set()
    unique = []
    for row in rows:
        key = (
            row.get("name", "").strip().lower(),
            row.get("address", "").strip().lower(),
            row.get("city", "").strip().lower()
        )
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique

if __name__ == "__main__":
    process_master_list()
