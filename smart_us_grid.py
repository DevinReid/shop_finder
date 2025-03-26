import csv

# U.S. bounds
LAT_START = 25.0
LAT_END = 49.0
LNG_START = -125.0
LNG_END = -66.0
SPACING_DEG = 0.27  # ~30km

OUTPUT_FILE = "grid_points.csv"

def generate_us_grid(lat_start, lat_end, lng_start, lng_end, spacing_deg):
    coords = []
    lat = lat_start
    while lat <= lat_end:
        lng = lng_start
        while lng <= lng_end:
            coords.append((round(lat, 4), round(lng, 4)))
            lng += spacing_deg
        lat += spacing_deg
    return coords

def save_grid_to_csv(coords, filename=OUTPUT_FILE):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["lat", "lng"])
        for lat, lng in coords:
            writer.writerow([lat, lng])
    print(f"✅ Saved {len(coords)} grid points to {filename}")

if __name__ == "__main__":
    grid = generate_us_grid(LAT_START, LAT_END, LNG_START, LNG_END, SPACING_DEG)
    save_grid_to_csv(grid)
