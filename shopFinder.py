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
API_KEY = "REMOVED_KEY"  # Replace with your key

SEARCH_LOG_FILE = "search_log.csv"
PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
MAX_MONTHLY_QUOTA = 10588
COUNTER_FILE = "usage_counter.txt"
OUTPUT_CSV = "master_list.csv"

# Cost per API call (in USD)
COST_PER_SEARCH = 0.017  # $0.017 per search
COST_PER_DETAILS = 0.017  # $0.017 per place details

# ----------------------
# SEARCH QUERIES & LOCATIONS
# ----------------------
city_searches = {
    # Fantasy/Pirate themed cities
    "Tampa": {
        "locations": [
            {"coords": "27.9506,-82.4572", "radius": 50000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    "St Augustine": {
        "locations": [
            {"coords": "29.9012,-81.3124", "radius": 50000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    "New Orleans": {  # NOLA
        "locations": [
            {"coords": "29.9511,-90.0715", "radius": 50000}
        ],
        "queries": ["fantasy gift shop", "witch store", "tabletop game store"]
    },
    "Beaufort": {
        "locations": [
            {"coords": "32.4316,-80.6698", "radius": 50000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    
    # Witch store cities
    "Salem": {
        "locations": [
            {"coords": "42.5195,-70.8967", "radius": 20000},  # Center point
            {"coords": "42.7895,-70.8967", "radius": 20000},  # North point (35km north)
            {"coords": "42.5195,-71.2967", "radius": 20000},  # East point (35km east)
            {"coords": "42.2495,-70.4967", "radius": 20000}   # Southwest point (35km southwest)
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    "Portland": {
        "locations": [
            {"coords": "45.5155,-122.6789", "radius": 20000},  # Downtown Portland
            {"coords": "45.7855,-122.6789", "radius": 20000},  # North point
            {"coords": "45.5155,-123.0789", "radius": 20000},  # East point
            {"coords": "45.2455,-121.8789", "radius": 20000}   # Southwest point
        ],
        "queries": ["witch store", "tabletop game store", "fantasy gift shop"]
    },
    "Los Angeles": {
        "locations": [
            {"coords": "34.0522,-118.2437", "radius": 20000},  # Downtown LA
            {"coords": "34.3222,-118.2437", "radius": 20000},  # North point
            {"coords": "34.0522,-118.6437", "radius": 20000},  # East point
            {"coords": "33.7822,-117.8437", "radius": 20000}   # Southwest point
        ],
        "queries": ["witch store", "tabletop game store", "fantasy gift shop"]
    },
    "New York City": {
        "locations": [
            {"coords": "40.7128,-74.0060", "radius": 20000},  # Manhattan
            {"coords": "40.9828,-74.0060", "radius": 20000},  # North point
            {"coords": "40.7128,-74.4060", "radius": 20000},  # East point
            {"coords": "40.4428,-73.6060", "radius": 20000}   # Southwest point
        ],
        "queries": ["witch store", "tabletop game store", "fantasy gift shop"]
    },
    "Seattle": {
        "locations": [
            {"coords": "47.6062,-122.3321", "radius": 20000},  # Downtown Seattle
            {"coords": "47.8762,-122.3321", "radius": 20000},  # North point
            {"coords": "47.6062,-122.7321", "radius": 20000},  # East point
            {"coords": "47.3362,-121.9321", "radius": 20000}   # Southwest point
        ],
        "queries": ["witch store", "tabletop game store", "fantasy gift shop"]
    },
    
    # Tabletop game cities
    "Orange County": {
        "locations": [
            {"coords": "33.7175,-117.8311", "radius": 30000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    "San Diego": {
        "locations": [
            {"coords": "32.7157,-117.1611", "radius": 30000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    "Austin": {
        "locations": [
            {"coords": "30.2672,-97.7431", "radius": 20000},  # Downtown Austin
            {"coords": "30.5372,-97.7431", "radius": 20000},  # North point
            {"coords": "30.2672,-98.1431", "radius": 20000},  # East point
            {"coords": "29.9972,-96.9431", "radius": 20000}   # Southwest point
        ],
        "queries": ["tabletop game store", "fantasy gift shop"]
    },
    
    # Fantasy cities (additional)
    "Atlanta": {
        "locations": [
            {"coords": "33.7490,-84.3880", "radius": 30000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    },
    "Chicago": {
        "locations": [
            {"coords": "41.8781,-87.6298", "radius": 30000}
        ],
        "queries": ["fantasy gift shop", "tabletop game store", "witch store"]
    }
}

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

def get_quota_usage():
    """Get current quota usage and remaining"""
    current_usage = get_usage_count()
    remaining = MAX_MONTHLY_QUOTA - current_usage
    usage_percent = (current_usage / MAX_MONTHLY_QUOTA) * 100
    
    return {
        "current_usage": current_usage,
        "remaining": remaining,
        "usage_percent": usage_percent
    }

def estimate_total_cost():
    """Estimate the total cost of running all searches"""
    total_searches = 0
    total_details = 0
    
    for city, data in city_searches.items():
        for query in data["queries"]:
            # Skip if already searched
            lat, lng = map(float, data["locations"][0]["coords"].split(","))
            if has_already_searched(query, city, lat, lng, data["locations"][0]["radius"]):  # Using default radius for check
                continue
                
            total_searches += 1
            # Assume average of 20 results per search (conservative estimate)
            total_details += 20
    
    search_cost = total_searches * COST_PER_SEARCH
    details_cost = total_details * COST_PER_DETAILS
    total_cost = search_cost + details_cost
    
    return {
        "total_searches": total_searches,
        "estimated_details": total_details,
        "search_cost": search_cost,
        "details_cost": details_cost,
        "total_cost": total_cost
    }

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
        # Add delay before each details request
        time.sleep(2)
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
    total_results = 0
    
    # Extract coordinates for location identifier
    lat, lng = map(float, location.split(","))
    location_id = f"{city_label}_{lat:.2f}_{lng:.2f}"

    while True:
        print(f"\n🔍 Search Location: {city_label} ({lat:.4f}, {lng:.4f})")
        print(f"📄 Searching page {page} for '{query}'...")
        try:
            # Add delay between requests
            if page > 1:
                print("⏳ Waiting 5 seconds before next request...")
                time.sleep(5)
                
            response = requests.get(PLACES_URL, params=params)
            data = response.json()

            if data.get("status") != "OK":
                print("⚠️ Google API Error:", data.get("error_message", data.get("status")))
                break

            results = data.get("results", [])
            total_results += len(results)
            
            for r in results:
                name = r.get("name")
                address = r.get("formatted_address")
                place_id = r.get("place_id")

                # Add delay between detail requests
                time.sleep(2)
                website = get_place_website(place_id)
                email = extract_email_from_website(website) if website else ""

                all_stores.append({
                    "name": name,
                    "address": address,
                    "website": website,
                    "email": email,
                    "query": query,
                    "city": city_label,
                    "location_id": location_id,
                    "coordinates": location
                })

            next_page_token = data.get("next_page_token")
            if next_page_token:
                time.sleep(3)  # Required by Google API
                params = {
                    "pagetoken": next_page_token,
                    "key": API_KEY
                }
                page += 1
                continue
            else:
                break

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)  # Increased retry delay
            continue

    return all_stores, total_results


# ----------------------
# SAVE TO CSV
# ----------------------
def is_duplicate(entry, existing_entries, current_search_only=True):
    """
    Check if an entry is a duplicate, optionally only checking against current search results
    """
    for other in existing_entries:
        if (current_search_only and 
            entry.get("query", "") != other.get("query", "") and 
            entry.get("city", "") != other.get("city", "")):
            continue
            
        if (entry.get("name", "").strip().lower() == other.get("name", "").strip().lower() and
            entry.get("address", "").strip().lower() == other.get("address", "").strip().lower() and
            entry.get("city", "").strip().lower() == other.get("city", "").strip().lower()):
            return True
    return False

def save_to_csv(stores, filename=OUTPUT_CSV):
    file_exists = os.path.isfile(filename)
    fieldnames = ["sorted", "query", "city", "location_id", "coordinates", "name", "address", "website", "email", "flagged"]

    # Track duplicates within current search
    current_entries = []
    duplicates_found = 0

    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for store in stores:
            row = {
                "sorted": "false",
                "query": store.get("query", ""),
                "city": store.get("city", ""),
                "location_id": store.get("location_id", ""),
                "coordinates": store.get("coordinates", ""),
                "name": store.get("name", ""),
                "address": store.get("address", ""),
                "website": store.get("website", ""),
                "email": store.get("email", ""),
                "flagged": ""
            }
            
            # Check for duplicates within current search only
            if is_duplicate(row, current_entries, current_search_only=True):
                duplicates_found += 1
                continue
                
            current_entries.append(row)
            writer.writerow(row)


# ----------------------
# OPTIMAL RADII TRACKING
# ----------------------
def save_optimal_radius(city, coords, query, radius, result_count):
    """Save successful search parameters to optimal_radii.csv"""
    file_exists = os.path.exists("optimal_radii.csv")
    with open("optimal_radii.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["city", "coordinates", "query", "radius", "result_count", "date"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "city": city,
            "coordinates": coords,
            "query": query,
            "radius": radius,
            "result_count": result_count,
            "date": time.strftime("%Y-%m-%d")
        })

def is_optimal_radius_saved(city, coords, query):
    """Check if we already have an optimal radius saved for this search"""
    if not os.path.exists("optimal_radii.csv"):
        return False
    with open("optimal_radii.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row["city"] == city and 
                row["coordinates"] == coords and 
                row["query"] == query):
                return True
    return False

# ----------------------
# MAIN LOGIC
# ----------------------
def find_optimal_radius(query, location, city_label, max_radius=50000, min_radius=1000, target_results=60):
    """
    Binary search to find the optimal radius that yields close to but not exceeding target_results
    """
    current_radius = max_radius
    min_radius_used = min_radius
    max_radius_used = max_radius
    best_radius = max_radius
    best_result_count = 0
    
    while min_radius_used <= max_radius_used:
        current_radius = (min_radius_used + max_radius_used) // 2
        print(f"🔍 Testing radius {current_radius}m for {city_label}...")
        
        params = {
            "query": query,
            "location": location,
            "radius": current_radius,
            "key": API_KEY
        }
        
        response = requests.get(PLACES_URL, params=params)
        data = response.json()
        
        if data.get("status") != "OK":
            print("⚠️ Google API Error:", data.get("error_message", data.get("status")))
            return max_radius, 0  # Fallback to max radius on error
        
        result_count = len(data.get("results", []))
        
        if result_count <= target_results:
            # This radius works, but let's try a larger one
            best_radius = current_radius
            best_result_count = result_count
            min_radius_used = current_radius + 1
        else:
            # Too many results, try a smaller radius
            max_radius_used = current_radius - 1
    
    print(f"✅ Found optimal radius {best_radius}m for {city_label} with {best_result_count} results")
    return best_radius, best_result_count

def run_search(query, location, city_label, radius=30000):
    lat, lng = map(float, location.split(","))
    
    # Check if we have an optimal radius saved (these are our ✅ results)
    if is_optimal_radius_saved(city_label, location, query):
        print(f"\n⏩ Skipping '{query}' in {city_label} - optimal radius already saved")
        return 0, 0

    if not is_quota_available(1):
        print("🚫 Quota exceeded — skipping this query.")
        return 0, 0

    print(f"\n📍 Search Location: {city_label} ({lat:.4f}, {lng:.4f})")
    print(f"🔎 Searching '{query}' with radius {radius}m")
    stores, total_results = find_stores(query, location, city_label, radius)

    if stores:
        # Count how many new emails were added
        new_emails = sum(1 for store in stores if store.get("email"))
        save_to_csv(stores)
        increment_usage(1)
        
        # Log the search for historical purposes
        log_search(query, city_label, lat, lng, radius)
        
        # Save optimal radius if this was a successful search
        # A search is successful if:
        # 1. We found 45-59 results (good sweet spot), OR
        # 2. We found <45 results at max radius (best we can do)
        if (45 <= total_results < 60) or (total_results < 45 and radius >= 50000):
            save_optimal_radius(city_label, location, query, radius, total_results)
            
        print(f"✅ Found {total_results} results, {new_emails} with emails")
        return total_results, new_emails
    else:
        print("No results found.")
        return 0, 0


# ----------------------
# RUN ALL COMBINATIONS
# ----------------------
if __name__ == "__main__":
    # Get current quota usage
    quota = get_quota_usage()
    
    # Estimate costs before running
    cost_estimate = estimate_total_cost()
    
    print("\n💰 Cost Estimate and Quota Usage:")
    print("=" * 50)
    print(f"Current API Usage: {quota['current_usage']:,} / {MAX_MONTHLY_QUOTA:,} requests ({quota['usage_percent']:.1f}% used)")
    print(f"Remaining requests: {quota['remaining']:,}")
    print("-" * 50)
    print(f"Total new searches to run: {cost_estimate['total_searches']}")
    print(f"Estimated place details to fetch: {cost_estimate['estimated_details']}")
    print(f"Search API cost: ${cost_estimate['search_cost']:.2f}")
    print(f"Details API cost: ${cost_estimate['details_cost']:.2f}")
    print(f"Total estimated cost: ${cost_estimate['total_cost']:.2f}")
    print("=" * 50)
    
    # Check if we have enough quota remaining
    if quota['remaining'] < (cost_estimate['total_searches'] + cost_estimate['estimated_details']):
        print("\n⚠️ Warning: This will exceed your monthly quota!")
        print(f"Need {cost_estimate['total_searches'] + cost_estimate['estimated_details']:,} requests")
        print(f"Only {quota['remaining']:,} requests remaining")
    
    proceed = input("\nDo you want to proceed? (y/n): ")
    if proceed.lower() != 'y':
        print("Search cancelled.")
        exit()
    
    # Track results for each location/query combination
    search_results = {}
    
    for city, data in city_searches.items():
        for location in data["locations"]:
            location_id = f"{city}_{location['coords']}"
            search_results[location_id] = {
                "radius": location["radius"],
                "queries": {}
            }
            
            for query in data["queries"]:
                total_results, new_emails = run_search(query, location["coords"], city, location["radius"])
                search_results[location_id]["queries"][query] = {
                    "total": total_results,
                    "emails": new_emails
                }

    print("\n✨ Running listCleaner after scrape...")
    process_master_list()

    print("\n🗺️ Generating map of searched areas...")
    generate_search_map()
    
    # Print detailed results summary
    print("\n📊 Search Results Summary:")
    print("=" * 80)
    print("Legend:")
    print("✅ - Good results (45-59 results, or <45 results at max radius)")
    print("⚠️ - Could find more results with larger radius (<45 results at non-max radius)")
    print("❌ - Too many results (60+ results, should use smaller radius)")
    print("=" * 80)
    
    for location_id, data in sorted(search_results.items()):
        city, coords = location_id.split("_", 1)
        lat, lng = coords.split(",")
        radius = data["radius"]
        print(f"\n📍 Location: {city} ({lat}, {lng}) - Radius: {radius}m")
        print("-" * 80)
        
        for query, counts in data["queries"].items():
            if counts["total"] >= 60:
                print(f"❌ {query}: {counts['total']} results ({counts['emails']} with emails) - too many results, try smaller radius")
            elif counts["total"] < 45 and radius < 50000:
                print(f"⚠️ {query}: {counts['total']} results ({counts['emails']} with emails) - could try larger radius")
            else:
                print(f"✅ {query}: {counts['total']} results ({counts['emails']} with emails)")
    
    print("\n" + "=" * 80)
