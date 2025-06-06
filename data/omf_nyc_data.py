import overturemaps, geopandas as gpd, pandas as pd, json
from shapely import wkt
from difflib import SequenceMatcher

# ────────────────────────────────────────────────────────────────
# 1. Overture “place” layer (NYC)
# ────────────────────────────────────────────────────────────────
bbox = (-74.25909, 40.477399, -73.700272, 40.917577)
gdf_place = overturemaps.core.geodataframe("place", bbox=bbox).cx[
    bbox[0]:bbox[2], bbox[1]:bbox[3]
]

def best_name(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    if isinstance(raw, str):
        s = raw.strip()
        if s and s[0] in "{[":
            try:   return best_name(json.loads(s))
            except Exception:  return s
        return s
    if isinstance(raw, dict):
        return raw.get("primary") or raw.get("name", "")
    if isinstance(raw, list):
        for n in raw:
            if isinstance(n, dict) and (n.get("primary") or n.get("name")):
                return n.get("primary") or n.get("name")
            if isinstance(n, str) and n.strip():
                return n.strip()
    if hasattr(raw, "primary"):
        return getattr(raw, "primary")
    return str(raw)

gdf_place["primary_name"] = gdf_place["names"].apply(best_name)

# ────────────────────────────────────────────────────────────────
# 2. NYC POI dataset
# ────────────────────────────────────────────────────────────────
poi_url = ("https://data.cityofnewyork.us/api/views/t95h-5fsr/"
           "rows.csv?accessType=DOWNLOAD")
df_poi   = pd.read_csv(poi_url, low_memory=False)
title_col = "FEATURE NAME"
geom = df_poi["the_geom"].dropna().apply(wkt.loads)
gdf_poi = gpd.GeoDataFrame(df_poi.loc[geom.index], geometry=geom, crs="EPSG:4326")

# ────────────────────────────────────────────────────────────────
# 3. Nearest-POI join (genuine nearest geometry)
# ────────────────────────────────────────────────────────────────
joined = gpd.sjoin_nearest(
    gdf_place[["primary_name", "geometry"]],
    gdf_poi[[title_col, "geometry"]],
    how="left",
    distance_col="match_dist_deg",
    max_distance=0.01
).rename(columns={title_col: "match_poi_name"})

# distance → metres  (85 km ≃ 1° at NYC latitude)
joined["match_dist_m"] = (joined["match_dist_deg"] * 85_000).round(1)

# ────────────────────────────────────────────────────────────────
# 4. wrong_conf  (vectorised)
# ────────────────────────────────────────────────────────────────
def sim(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

name_similarity = joined.apply(
    lambda r: 0.0 if pd.isna(r["match_poi_name"]) or not r["match_poi_name"].strip()
    else sim(r["primary_name"], r["match_poi_name"]),
    axis=1
)

score_dist  = (joined["match_dist_m"] / 250).clip(upper=1)          # 0-1
score_name  = 1 - name_similarity.replace(0, 0.5)                   # blanks → 0.5
joined["wrong_conf"] = (0.6 * score_dist + 0.4 * score_name).round(2)

# ────────────────────────────────────────────────────────────────
# 5. Quick looks
# ────────────────────────────────────────────────────────────────
print("\n▶ Random sample of 10")
print(joined.sample(10, random_state=0)[
        ["primary_name", "match_poi_name", "match_dist_m", "wrong_conf"]
    ].to_markdown())

print("\n▶ Top 10 highest wrong_conf")
print(joined.sort_values("wrong_conf", ascending=False).head(10)[
        ["primary_name", "match_poi_name", "match_dist_m", "wrong_conf"]
    ].to_markdown())

print("\nTotal suspects (wrong_conf > 0.7):",
      (joined["wrong_conf"] > 0.7).sum())
