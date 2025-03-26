import requests
import csv
import os
import re
from bs4 import BeautifulSoup
import time
from listCleaner import process_master_list

# ----------------------
# CONFIGURATION
# ----------------------
API_KEY = "AIzaSyDavZr62SbyNOKqmPIi0MnOjyGMYeI5EaM"  # Replace with your keyfrom listCleaner import process_master_list

PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
MAX_MONTHLY_QUOTA = 10588
COUNTER_FILE = "usage_counter.txt"
OUTPUT_CSV = "master_list.csv"

# ----------------------
# SEARCH QUERIES & LOCATIONS
# ----------------------
queries = [
    # "fantasy gift shop",
    # "dice store",
    # "witch store",
    "tabletop game store"
]

coordinates = [
    # ("New York City", "40.7128,-74.0060"),
    # ("Los Angeles", "34.0522,-118.2437"),
    ("Chicago", "41.8781,-87.6298"),
]

# ----------------------
# USAGE TRACKING
# ----------------------
def get_usage_count():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def increment_usage(count):
    current = get_usage_count()
    with open(COUNTER_FILE, "w") as f:
        f.write(str(current + count))

def is_quota_available(requests_needed):
    return get_usage_count() + requests_needed <= MAX_MONTHLY_QUOTA

# ----------------------
# EMAIL SCRAPER
# ----------------------
def extract_email_from_website(url):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        emails = set(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', soup.get_text()))
        return list(emails)[0] if emails else ""
    except Exception as e:
        print(f"❌ Failed to scrape email from {url}: {e}")
        return ""

# ----------------------
# PLACE DETAILS API CALL
# ----------------------
def get_place_website(place_id):
    params = {
        "place_id": place_id,
        "fields": "website",
        "key": API_KEY
    }
    try:
        response = requests.get(DETAILS_URL, params=params)
        data = response.json()
        website = data.get("result", {}).get("website", "")
        return website
    except Exception as e:
        print(f"❌ Failed to fetch website for {place_id}: {e}")
        return ""

# ----------------------
# GOOGLE PLACES SEARCH (1st page only, with pagination commented)
# ----------------------
def find_stores(query, location, city_label, radius=50000):
    params = {
        "query": query,
        "location": location,
        "radius": radius,
        "key": API_KEY
    }

    all_stores = []
    page = 1

    while True:
        print(f"📄 Page {page} for '{query}' in {city_label}...")
        response = requests.get(PLACES_URL, params=params)
        data = response.json()

        if data.get("status") != "OK":
            print("⚠️ Google API Error:", data.get("error_message", data.get("status")))
            break

        results = data.get("results", [])
        for r in results:
            name = r.get("name")
            address = r.get("formatted_address")
            place_id = r.get("place_id")

            website = get_place_website(place_id)
            email = extract_email_from_website(website) if website else ""

            all_stores.append({
                "name": name,
                "address": address,
                "website": website,
                "email": email,
                "query": query,
                "city": city_label
            })

        next_page_token = data.get("next_page_token")
        if next_page_token:
            print(f"➡️ Next page token found: {next_page_token}")
            # Uncomment below to enable pagination (Google requires short wait)
            # time.sleep(3)
            # params = {
            #     "pagetoken": next_page_token,
            #     "key": API_KEY
            # }
            # page += 1
            # continue
            break
        else:
            break

    return all_stores

# ----------------------
# SAVE TO CSV
# ----------------------
def save_to_csv(stores, filename=OUTPUT_CSV):
    file_exists = os.path.isfile(filename)
    fieldnames = ["sorted", "query", "city", "name", "address", "website", "email", "flagged"]

    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for store in stores:
            row = {
                "sorted": "false",
                "query": store.get("query", ""),
                "city": store.get("city", ""),
                "name": store.get("name", ""),
                "address": store.get("address", ""),
                "website": store.get("website", ""),
                "email": store.get("email", ""),
                "flagged": ""
            }
            writer.writerow(row)


# ----------------------
# MAIN LOGIC
# ----------------------
def run_search(query, location, city_label):
    if not is_quota_available(1):
        print("🚫 Quota exceeded — skipping this query.")
        return

    print(f"\n🔎 Searching '{query}' near {city_label}")
    stores = find_stores(query, location, city_label)

    if stores:
        save_to_csv(stores)
        increment_usage(1)
        print(f"✅ Saved {len(stores)} results to {OUTPUT_CSV}")
    else:
        print("No results found.")

# ----------------------
# RUN ALL COMBINATIONS
# ----------------------
if __name__ == "__main__":
    for query in queries:
        for city_name, coords in coordinates:
            run_search(query, coords, city_name)

    print("\n✨ Running listCleaner after scrape...")
    process_master_list()
