import os
import numpy as np
import geopandas as gpd

DATA_PROCESSED = "data/processed"
input_path = os.path.join(DATA_PROCESSED, "wayanad_hazard_layer.gpkg")

print("[1/3] Loading hazard layer...")
gdf = gpd.read_file(input_path, layer="hazard_cells")

def min_max_normalize(series):
    s_min, s_max = series.min(), series.max()
    if s_max == s_min:
        return np.zeros(len(series))
    return 100.0 * (series - s_min) / (s_max - s_min)

print("[2/3] Calculating Exposure and Vulnerability indices...")
# 1. Exposure Score: High population presence + road access
pop_norm = min_max_normalize(gdf["population"])
road_prox_norm = 100.0 - min_max_normalize(gdf["dist_road_m"])
gdf["exposure_score"] = (0.70 * pop_norm + 0.30 * road_prox_norm).round(2)

# 2. Vulnerability Score: Poverty + Demographics + Isolation from Healthcare
pov_norm = min_max_normalize(gdf["poverty_rate"])
demo_norm = min_max_normalize(gdf["vulnerable_pop_ratio"])
health_dist_norm = min_max_normalize(gdf["dist_health_m"])

gdf["vulnerability_score"] = (
    0.40 * pov_norm + 0.35 * demo_norm + 0.25 * health_dist_norm
).round(2)

print("[3/3] Deriving Multi-Hazard Risk and Priority Classification...")
# Weighted Risk Formula
gdf["risk_score"] = (
    0.45 * gdf["hazard_score"] +
    0.30 * gdf["exposure_score"] +
    0.25 * gdf["vulnerability_score"]
).round(2)

# Classification buckets
def classify_risk(score):
    if score >= 80.0:
        return "Critical"
    elif score >= 60.0:
        return "Very High"
    elif score >= 40.0:
        return "High"
    elif score >= 20.0:
        return "Moderate"
    else:
        return "Low"

def relocation_action(score, pop):
    if pop <= 0:
        return "No Action"
    if score >= 85.0:
        return "Immediate Relocation"
    elif score >= 70.0:
        return "Short-term Relocation"
    elif score >= 50.0:
        return "Monitor"
    else:
        return "No Action"

gdf["risk_category"] = gdf["risk_score"].apply(classify_risk)
gdf["relocation_priority"] = [
    relocation_action(r, p) for r, p in zip(gdf["risk_score"], gdf["population"])
]

# Save updated risk layer
output_path = os.path.join(DATA_PROCESSED, "wayanad_risk_layer.gpkg")
gdf.to_file(output_path, layer="risk_cells", driver="GPKG")

# Summary output
counts = gdf["relocation_priority"].value_counts().to_dict()
print(f"\n--- Risk Scoring Completed ---")
print(f"Relocation Priorities breakdown: {counts}")
print(f"Saved risk layer to: {output_path}")