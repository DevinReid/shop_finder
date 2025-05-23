import csv
import re
import os


# Known TLDs for email boundary
TLDs = "com|net|org|edu|io|co|us|biz|store|shop|info"

# Common prefixes that might indicate a placeholder or system email
SUSPICIOUS_PREFIXES = [
    'service', 'contact', 'info', 'help', 'usemail', 'support', 'team', 'admin'
]

# File paths
MASTER_FILE = "master_list.csv"
WITH_EMAILS_FILE = "stores_with_emails.csv"
WITHOUT_EMAILS_FILE = "stores_without_email.csv"

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
    "sorted", "query", "city", "name", "address", "website", "email", "flagged"
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
