import requests
import csv
import os
import re
from bs4 import BeautifulSoup
import time
from listCleaner import process_master_list
from map_search_log import generate_search_map

# ----------------------
# CONFIGURATION
# ----------------------
API_KEY = "REMOVED_KEY"  # Replace with your keyfrom listCleaner import process_master_listfrom map_search_log import generate_search_map


SEARCH_LOG_FILE = "search_log.csv"
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
    ("New Orleans", "29.9511,-90.0715")
]


def has_already_searched(query, city, lat, lng, radius):
    if not os.path.exists(SEARCH_LOG_FILE):
        return False
    with open(SEARCH_LOG_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (
                row["query"] == query and
                row["city"] == city and
                abs(float(row["lat"]) - float(lat)) < 0.0001 and
                abs(float(row["lng"]) - float(lng)) < 0.0001 and
                int(row["radius_m"]) == radius
            ):
                return True  # ✅ Confirmed: this exact search was already *completed* and logged
    return False  # Otherwise, let it run again


def log_search(query, city, lat, lng, radius):
    file_exists = os.path.exists(SEARCH_LOG_FILE)
    with open(SEARCH_LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["query", "city", "lat", "lng", "radius_m", "date"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "query": query,
            "city": city,
            "lat": lat,
            "lng": lng,
            "radius_m": radius,
            "date": time.strftime("%Y-%m-%d")
        })



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
            time.sleep(3)
            params = {
                "pagetoken": next_page_token,
                "key": API_KEY
            }
            page += 1
            continue
            break
        else:
            break

    return all_stores, not bool(next_page_token)  # complete = True if no next page


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
def run_search(query, location, city_label, radius=30000):
    lat, lng = map(float, location.split(","))
    if has_already_searched(query, city_label, lat, lng, radius):
        print(f"⏩ Already searched '{query}' near {city_label} ({lat}, {lng})")
        return

    if not is_quota_available(1):
        print("🚫 Quota exceeded — skipping this query.")
        return

    print(f"\n🔎 Searching '{query}' near {city_label}")
    stores, complete = find_stores(query, location, city_label, radius)

    if stores:
        save_to_csv(stores)
        increment_usage(1)
        if complete:
            log_search(query, city_label, lat, lng, radius)
            print(f"✅ Finished and logged search for '{query}' near {city_label}")
        else:
            print(f"⚠️ Partial results only — not logging yet (next page likely exists)")
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

    print("\n🗺️ Generating map of searched areas...")
    generate_search_map()
