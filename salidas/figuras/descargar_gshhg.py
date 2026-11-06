#!/usr/bin/env python3
"""Descarga polígonos de tierra de GSHHG High Resolution para Chile.

Usa el ArcGIS REST FeatureServer de GSHHG High Resolution.
Guarda en /tmp/opencode/gshhg_chile/gshhg_chile_high.shp
"""
import json
import time
from pathlib import Path

import geopandas as gpd
import requests
from shapely.geometry import shape

OUT = Path("/tmp/opencode/gshhg_chile")
OUT.mkdir(parents=True, exist_ok=True)
URL = "https://services7.arcgis.com/WSiUmUhlFx4CtMBB/arcgis/rest/services/GSHHS_GlobalCoastlines_HighResolution/FeatureServer/0/query"

bbox = "-76,-55,-66,-40"
all_features = []
offset = 0
batch = 2000
while True:
    params = {
        "where": "1=1",
        "geometry": bbox,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "OBJECTID",
        "returnGeometry": "true",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": batch,
    }
    r = requests.get(URL, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()
    feats = data.get("features", [])
    if not feats:
        break
    all_features.extend(feats)
    print(f"  offset {offset}: {len(feats)} features (total {len(all_features)})")
    if len(feats) < batch:
        break
    offset += batch
    time.sleep(1)

# guardar como GeoJSON
geojson = {"type": "FeatureCollection", "features": all_features}
out_geojson = OUT / "gshhg_chile_high.geojson"
with open(out_geojson, "w") as f:
    json.dump(geojson, f)
print("GeoJSON:", out_geojson, len(all_features), "features")

# convertir a GeoDataFrame y guardar como shapefile
gdf = gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")
shp = OUT / "gshhg_chile_high.shp"
gdf.to_file(shp)
print("Shapefile:", shp, gdf.shape)
print("geom types:", gdf.geom_type.value_counts().to_dict())