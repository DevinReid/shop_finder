import math

# Subdivision rules: {parent_radius: (child_radius, number_of_subcircles)}
SUBDIVISION_RULES = {
    50000: (25000, 6),  # 50km -> 6 circles of 25km
    25000: (13000, 5),  # 25km -> 5 circles of 13km
    13000: (6000, 7),   # 13km -> 7 circles of 6km
    6000: (3000, 7),    # 6km -> 7 circles of 3km
    3000: (1500, 7)     # 3km -> 7 circles of 1.5km
}

def generate_child_centers(lat, lng, parent_radius, child_radius, count):
    """Generate coordinates of child circle centers using fixed offsets."""
    centers = []
    
    # Calculate the offset distance in degrees
    # 1 degree of latitude is approximately 111km
    # 1 degree of longitude varies with latitude, but we'll use a conservative estimate
    lat_offset = (parent_radius - child_radius) / 111000  # Convert meters to degrees
    lng_offset = lat_offset / math.cos(math.radians(lat))  # Adjust for longitude
    
    if count in [5, 6]:  # Simple ring layout
        # For 5 or 6 circles, arrange them in a ring
        for i in range(count):
            angle = i * 2 * math.pi / count
            new_lat = lat + lat_offset * math.sin(angle)
            new_lng = lng + lng_offset * math.cos(angle)
            centers.append((new_lat, new_lng, child_radius))
    
    elif count == 7:  # Center + hex ring
        # For 7 circles, place one in center and 6 in a ring
        centers.append((lat, lng, child_radius))  # Center circle
        for i in range(6):
            angle = i * math.pi / 3  # 60 degrees
            new_lat = lat + lat_offset * math.sin(angle)
            new_lng = lng + lng_offset * math.cos(angle)
            centers.append((new_lat, new_lng, child_radius))
    
    return centers

def get_subdivision_centers(lat, lng, radius):
    """
    Get subdivision centers for a given coordinate and radius.
    Returns a list of (lat, lng, radius) tuples for new search areas.
    """
    if radius not in SUBDIVISION_RULES:
        return []
        
    child_radius, count = SUBDIVISION_RULES[radius]
    return generate_child_centers(lat, lng, radius, child_radius, count)

def should_subdivide(radius, result_count):
    """
    Determine if a search area should be subdivided based on its radius and result count.
    """
    return radius in SUBDIVISION_RULES and result_count >= 60 