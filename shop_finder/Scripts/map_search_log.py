# map_search_log.py
import folium
import csv
from shop_finder.config import FILES
from collections import defaultdict

def generate_search_map(log_file=FILES["search_log"], output_file="search_map.html"):
    # Set up base map
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=5)
    query_layers = defaultdict(lambda: folium.FeatureGroup(name="unknown", show=True))

    with open(log_file, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = row["query"]
            city = row["city"]
            lat = float(row["lat"])
            lng = float(row["lng"])
            radius_m = int(row["radius_m"])

            popup_text = f"{query}<br>{city}<br>{radius_m} meters"
            circle = folium.Circle(
                location=[lat, lng],
                radius=radius_m,
                color="blue",
                fill=True,
                fill_opacity=0.4,
                popup=folium.Popup(popup_text, max_width=300)
            )

            layer_name = f"{query}"
            query_layers[layer_name].add_child(circle)

    for layer in query_layers.values():
        m.add_child(layer)

    folium.LayerControl().add_to(m)
    m.save(output_file)
    print(f"✅ Map saved to {output_file}")

# Optional: run as script
if __name__ == "__main__":
    generate_search_map()
