import csv
from config import FILES

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

def clean_retailer_files():
    """Create clean versions of the retailer files with excluded retailers removed"""
    # Load excluded retailers
    excluded_retailers = load_excluded_retailers()
    print(f"📋 Loaded {len(excluded_retailers)} excluded retailers")
    
    # Process each file
    files_to_process = [
        (FILES["with_emails"], "saki_search/saki_clean_with_emails.csv"),
        (FILES["without_emails"], "saki_search/saki_clean_without_emails.csv")
    ]
    
    # Fields to remove from output
    fields_to_remove = ["coordinates", "location_id"]
    
    total_removed = 0
    
    for input_file, output_file in files_to_process:
        kept_entries = []
        removed_count = 0
        
        # Read input file
        with open(input_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Get fieldnames and remove unwanted fields
            fieldnames = [field for field in reader.fieldnames if field not in fields_to_remove]
            
            # Process each entry
            for row in reader:
                if is_excluded_retailer(row["name"], excluded_retailers):
                    removed_count += 1
                    continue
                
                # Create new row without unwanted fields
                clean_row = {field: row[field] for field in fieldnames}
                kept_entries.append(clean_row)
        
        # Sort entries by city
        kept_entries.sort(key=lambda x: x["city"].lower())
        
        # Write output file
        with open(output_file, 'w', newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(kept_entries)
        
        # Count entries per city
        city_counts = {}
        for entry in kept_entries:
            city = entry["city"]
            city_counts[city] = city_counts.get(city, 0) + 1
        
        print(f"\n📊 Results for {input_file}:")
        print(f"   - Removed {removed_count} excluded retailers")
        print(f"   - Kept {len(kept_entries)} entries")
        print(f"   - Removed fields: {', '.join(fields_to_remove)}")
        print(f"   - Saved to {output_file}")
        print("\n   📍 Entries per city:")
        for city, count in sorted(city_counts.items()):
            print(f"      - {city}: {count}")
        
        total_removed += removed_count
    
    print(f"\n✨ Total retailers removed: {total_removed}")

if __name__ == "__main__":
    print("🧹 Starting retailer cleaning process...")
    clean_retailer_files()
    print("\n✅ Cleaning complete!") 