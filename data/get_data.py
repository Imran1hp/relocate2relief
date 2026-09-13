import os
import osmnx as ox
import geopandas as gpd

# Define directories
DATA_RAW = "data/raw"
os.makedirs(DATA_RAW, exist_ok=True)

print("[1/3] Fetching Wayanad District Boundary...")
# Query OpenStreetMap for the official boundary of Wayanad District
query = "Wayanad, Kerala, India"
boundary = ox.geocode_to_gdf(query)

# Ensure output CRS is WGS84 (EPSG:4326)
boundary = boundary.to_crs(epsg=4326)
boundary_file = os.path.join(DATA_RAW, "wayanad_boundary.geojson")
boundary.to_file(boundary_file, driver="GeoJSON")
print(f"Boundary saved: {boundary_file}")

print("[2/3] Fetching Roads & Infrastructure Network...")
# Download primary, secondary, and trunk roads within the boundary
roads = ox.features_from_place(query, tags={"highway": ["trunk", "primary", "secondary", "tertiary"]})
roads = roads[["highway", "geometry"]].to_crs(epsg=4326)
roads_file = os.path.join(DATA_RAW, "wayanad_roads.geojson")
roads.to_file(roads_file, driver="GeoJSON")
print(f"Roads saved: {roads_file}")

print("[3/3] Fetching Healthcare & Critical Facilities...")
# Download hospitals and clinics for carrying capacity and suitability analysis
health = ox.features_from_place(query, tags={"amenity": ["hospital", "clinic"]})
health = health[["amenity", "name", "geometry"]].to_crs(epsg=4326)
health_file = os.path.join(DATA_RAW, "wayanad_health.geojson")
health.to_file(health_file, driver="GeoJSON")
print(f"Healthcare points saved: {health_file}")

print("\n--- Data Ingestion Complete ---")