#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auditoría de solo lectura de la capa zonas_macrofauna (GPKG).
No escribe ni modifica el GPKG: abre con pyogrio en modo lectura.

Salida: reporte por stdout + CSVs en salidas/auditoria/
"""
import sys, json, os
import pandas as pd
import geopandas as gpd
import shapely
from shapely.ops import unary_union
from pyproj import CRS, Transformer
import pyogrio

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
GPKG = f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg"
LAYER = "zonas_macrofauna"
COUNTRIES = f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp"
CSV = f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv"
OUT = f"{BASE}/salidas/auditoria"
os.makedirs(OUT, exist_ok=True)

TOL_KM2 = 0.001  # criterio: < 0.001 km2 == cero

def sep(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)

sep("0. VERSIONES")
print("python      :", sys.version.split()[0])
print("geopandas   :", gpd.__version__)
print("shapely     :", shapely.__version__)
print("pyogrio     :", pyogrio.__version__)
import pyproj
print("pyproj      :", pyproj.__version__)
print("GDAL (pyogrio):", pyogrio.__gdal_version_string__)

# ---------------------------------------------------------------- 1. lectura
sep("1. LECTURA E INVENTARIO DE LA CAPA")
info = pyogrio.read_info(GPKG, layer=LAYER)
print("read_info:", json.dumps({k: v for k, v in info.items() if k in
      ("crs", "geometry_type", "features", "fields", "total_bounds")}, default=str, indent=2))

g = gpd.read_file(GPKG, layer=LAYER, engine="pyogrio")
print("\nfeatures leídas      :", len(g))
print("columnas             :", list(g.columns))
print("tipo geometría (gpd) :", g.geom_type.value_counts().to_dict())
print("CRS                  :", g.crs.to_string() if g.crs else "SIN CRS")
print("EPSG                 :", g.crs.to_epsg() if g.crs else None)
print("CRS es geográfico    :", g.crs.is_geographic if g.crs else None)
print("bounds (lon/lat)     :", g.total_bounds.tolist())

# --- validez geométrica (en el CRS original, es topológica y no depende de proyección)
sep("1b. VALIDEZ TOPOLÓGICA (CRS original EPSG:4326)")
g["is_valid"] = g.geometry.is_valid
g["is_empty"] = g.geometry.is_empty
g["is_null"] = g.geometry.isna()
g["valid_reason"] = [
    "OK" if v else shapely.is_valid_reason(geom) if geom is not None else "NULL"
    for v, geom in zip(g.is_valid, g.geometry)
]
print(g[["zona_mf", "is_valid", "is_empty", "is_null", "valid_reason"]].to_string(index=False))
n_inv = int((~g.is_valid).sum()); n_emp = int(g.is_empty.sum()); n_nul = int(g.is_null.sum())
print(f"\nresumen -> inválidas: {n_inv} | vacías: {n_emp} | nulas: {n_nul}")

# ------------------------------------------------------- 2. reproyecciones
sep("2. PROYECCIONES MÉTRICAS")
CRS_ALBERS = CRS.from_user_input("ESRI:102033")   # South America Albers Equal Area
CRS_EA_GLOBAL = CRS.from_user_input("EPSG:6933")  # EASE-Grid 2.0, área equivalente
CRS_UTM19S = CRS.from_user_input("EPSG:32719")    # WGS84/UTM 19S
for c in (CRS_ALBERS, CRS_EA_GLOBAL, CRS_UTM19S):
    print(f"  {c.to_string():<55} unidades={c.axis_info[0].unit_name} area_eq={c.is_projected}")

# para cálculo se usan geometrías validadas (make_valid) sin modificar el archivo
g["geom_ok"] = [shapely.make_valid(x) if x is not None else x for x in g.geometry]
_a = shapely.get_type_id(list(g.geometry.values))
_b = shapely.get_type_id(list(g.geom_ok.values))
_aa = shapely.area(list(g.geometry.values))
_ba = shapely.area(list(g.geom_ok.values))
print("\nmake_valid aplicado solo en memoria para el cálculo de áreas.")
print("¿alguna geometría cambió al aplicarlo? ", bool((_a != _b).any() or (_aa != _ba).any()))

gg = gpd.GeoDataFrame(
    g.drop(columns=["geometry"]),
    geometry=gpd.GeoSeries(list(g.geom_ok), crs="EPSG:4326", index=g.index),
    crs="EPSG:4326",
)
print("CRS tras reconstruir GeoDataFrame:", gg.crs.to_epsg())
ga = gg.to_crs(CRS_ALBERS)
ge = gg.to_crs(CRS_EA_GLOBAL)
gu = gg.to_crs(CRS_UTM19S)

# ------------------------------------------------- 3. áreas por zona
sep("3. ÁREA POR ZONA (Albers Sudamérica ESRI:102033 = área equivalente)")
res = pd.DataFrame({
    "zona_mf": g.zona_mf,
    "area_km2_albers": ga.area / 1e6,
    "area_km2_ease": ge.area / 1e6,
    "area_km2_utm19s": gu.area / 1e6,
})
res["diff_ease_%"] = (res.area_km2_ease - res.area_km2_albers) / res.area_km2_albers * 100
res["diff_utm_%"] = (res.area_km2_utm19s - res.area_km2_albers) / res.area_km2_albers * 100
print(res.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\nSUMA de áreas (Albers)     : {res.area_km2_albers.sum():,.4f} km²")
print(f"SUMA de áreas (EASE 6933)  : {res.area_km2_ease.sum():,.4f} km²")
print(f"SUMA de áreas (UTM 19S)    : {res.area_km2_utm19s.sum():,.4f} km²")

# --- control independiente: área geodésica sobre el elipsoide WGS84 (no depende de proyección)
from pyproj import Geod
geod = Geod(ellps="WGS84")
geo_km2 = []
for geom in g.geom_ok:
    a, _ = geod.geometry_area_perimeter(geom)
    geo_km2.append(abs(a) / 1e6)
res["area_km2_geodesica"] = geo_km2
res["diff_geod_albers_%"] = (res.area_km2_geodesica - res.area_km2_albers) / res.area_km2_geodesica * 100
print(f"\nCONTROL GEODÉSICO (elipsoide WGS84, pyproj.Geod) -> suma: {sum(geo_km2):,.4f} km²")
print("  desviación relativa de la proyección Albers respecto a la geodésica:")
print(f"  min {res['diff_geod_albers_%'].min():.4f}% | max {res['diff_geod_albers_%'].max():.4f}% "
      f"| media {res['diff_geod_albers_%'].mean():.4f}%")

# ------------------------------------------------- 4. solapamiento
sep("4. SOLAPAMIENTO ENTRE ZONAS")
u_albers = unary_union(list(ga.geometry))
area_union = u_albers.area / 1e6
suma = res.area_km2_albers.sum()
print(f"suma de áreas de las 20 zonas : {suma:,.4f} km²")
print(f"área de la UNIÓN              : {area_union:,.4f} km²")
print(f"solapamiento (suma - unión)   : {suma - area_union:,.4f} km²")
print(f"  -> % del área media         : {(suma-area_union)/suma*100:.4f}%")

# solapamiento por pares (evidencia)
pairs = []
for i in range(len(ga)):
    for j in range(i + 1, len(ga)):
        a = ga.geometry.iloc[i].intersection(ga.geometry.iloc[j]).area / 1e6
        if a > TOL_KM2:
            pairs.append((g.zona_mf.iloc[i], g.zona_mf.iloc[j], a))
pairs.sort(key=lambda t: -t[2])
if pairs:
    print("\nPares con solape > 0,001 km²:")
    for p in pairs:
        print(f"  {p[0]:<16} ∩ {p[1]:<16} = {p[2]:,.4f} km²")
    print(f"  suma de pares = {sum(p[2] for p in pairs):,.4f} km² (no equivale al solape múltiple)")
else:
    print("\nNo hay pares de zonas con solape > 0,001 km².")

# ------------------------------------------------- 5. partes y extensión
sep("5. PARTES, HUECOS Y EXTENSIÓN POR ZONA")
rows = []
for i, r in g.iterrows():
    geom = r.geom_ok
    gt = geom.geom_type
    if gt == "MultiPolygon":
        parts = list(geom.geoms)
    elif gt == "Polygon":
        parts = [geom]
    elif gt == "GeometryCollection":
        parts = [x for x in geom.geoms if x.geom_type in ("Polygon", "MultiPolygon")]
        parts = [p for x in parts for p in (list(x.geoms) if x.geom_type == "MultiPolygon" else [x])]
    else:
        parts = []
    n_parts = len(parts)
    n_holes = sum(len(p.interiors) for p in parts)
    gt4 = geom.geom_type
    # extensión = bbox de la zona en grados y en km (Albers)
    minx, miny, maxx, maxy = geom.bounds
    minpx, minpy, maxpx, maxpy = ga.geometry.iloc[i].bounds
    rows.append({
        "zona_mf": r.zona_mf,
        "geom_type": gt4,
        "n_partes": n_parts,
        "n_huecos": n_holes,
        "lon_min": minx, "lon_max": maxx, "lat_min": miny, "lat_max": maxy,
        "ancho_km": (maxpx - minpx) / 1e3,
        "alto_km": (maxpy - minpy) / 1e3,
        "perimetro_km": ga.geometry.iloc[i].length / 1e3,
    })
ext = pd.DataFrame(rows)
print(ext.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print("\npartes por zona -> total de partes:", int(ext.n_partes.sum()),
      "| zonas con >1 parte:", int((ext.n_partes > 1).sum()),
      "| huecos totales:", int(ext.n_huecos.sum()))

b = g.total_bounds
print(f"\nEXTENSIÓN TOTAL capa (EPSG:4326): lon [{b[0]:.6f}, {b[2]:.6f}]  lat [{b[1]:.6f}, {b[3]:.6f}]")
ba = u_albers.bounds
print(f"EXTENSIÓN TOTAL unión (Albers m): x [{ba[0]:,.0f}, {ba[2]:,.0f}]  y [{ba[1]:,.0f}, {ba[3]:,.0f}]")
print(f"  ancho {((ba[2]-ba[0])/1e3):,.1f} km | alto {((ba[3]-ba[1])/1e3):,.1f} km")
print(f"  bbox unión área = {((ba[2]-ba[0])*(ba[3]-ba[1]))/1e6:,.1f} km² "
      f"(llenado = {area_union/(((ba[2]-ba[0])*(ba[3]-ba[1]))/1e6)*100:.1f}%)")

# ------------------------------------------- 6. países que intersectan bbox
sep("6. INTERSECCIÓN CON LA UNIÓN DE TODOS LOS PAÍSES DEL BBOX")
c = gpd.read_file(COUNTRIES, engine="pyogrio")
print("países en la capa mundial:", len(c), "| CRS:", c.crs.to_epsg(),
      "| geom types:", c.geom_type.value_counts().to_dict())
bb = shapely.box(*g.total_bounds).buffer(0.5)  # bbox de zonas + 0.5° de margen
sel = c[c.geometry.intersects(bb)].copy()
cols = [x for x in ["ADMIN", "SOVEREIGNT", "ISO_A3", "CONTINENT"] if x in sel.columns]
print(f"\npaíses que intersectan el bbox de las zonas (+0,5° margen): {len(sel)}")
print(sel[cols].to_string(index=False))

# validar y unir todos los países
sel["geom_ok"] = [shapely.make_valid(x) for x in sel.geometry]
print("\npaíses con geometría inválida:", int((~sel.geometry.is_valid).sum()))
world_land = unary_union(list(sel.geom_ok))
print("tipo de la unión de países:", world_land.geom_type,
      "| válida:", world_land.is_valid, "| vacía:", world_land.is_empty)

land_a = gpd.GeoSeries([world_land], crs=4326).to_crs(CRS_ALBERS).iloc[0]
g["geom_land_inter"] = [x.intersection(land_a) for x in ga.geometry]
land_km2 = [x.area / 1e6 for x in g.geom_land_inter]

# por país
land_by_country = {}
for _, row in sel.iterrows():
    cg = gpd.GeoSeries([row.geom_ok], crs=4326).to_crs(CRS_ALBERS).iloc[0]
    land_by_country[row.ADMIN] = [x.intersection(cg).area / 1e6 for x in ga.geometry]

tbl = pd.DataFrame({"zona_mf": g.zona_mf,
                    "area_total_km2": ga.area / 1e6,
                    "area_en_tierra_km2": land_km2})
for name, vals in land_by_country.items():
    s = pd.Series(vals)
    if s.max() > TOL_KM2:
        tbl[f"tierra_{name}_km2"] = vals
tbl["residual_fuera_tierra_km2"] = tbl.area_total_km2 - tbl.area_en_tierra_km2
tbl["residual_%"] = tbl.residual_fuera_tierra_km2 / tbl.area_total_km2 * 100
# aplicar criterio de cero
for col in [c for c in tbl.columns if c.endswith("_km2")] + ["residual_%"]:
    tbl[col] = tbl[col].mask(tbl[col].abs() < TOL_KM2, 0.0)
print("\n--- INTEGRIDAD: área de cada zona dentro de la unión de países ---")
print(tbl.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

print(f"\nÁREA TOTAL de las zonas          : {tbl.area_total_km2.sum():,.4f} km²")
print(f"ÁREA dentro de la unión de países: {tbl.area_en_tierra_km2.sum():,.4f} km²")
print(f"ÁREA RESIDUAL (fuera de todo país): {tbl.residual_fuera_tierra_km2.sum():,.4f} km²"
      f"  ({tbl.residual_fuera_tierra_km2.sum()/tbl.area_total_km2.sum()*100:.4f}%)")
for name in land_by_country:
    tot = tbl.get(f"tierra_{name}_km2", pd.Series([0.0])).sum()
    if tot > 0:
        print(f"  dentro de {name:<12}: {tot:,.4f} km²")

# ¿algún bbox de zona toca tierra fuera del bbox ampliado?
sep("6b. CONTROL: ¿faltó algún país fuera del bbox+0,5°?")
far = c[~c.index.isin(sel.index)]
land_far = unary_union([shapely.make_valid(x) for x in far.geometry])
far_a = gpd.GeoSeries([land_far], crs=4326).to_crs(CRS_ALBERS).iloc[0]
extra = sum(x.intersection(far_a).area / 1e6 for x in ga.geometry)
print(f"área de zonas dentro de países NO incluidos en el bbox+0,5°: {extra:,.6f} km²")
print("(si es 0.000000, la selección de países fue exhaustiva)")

# --------------------------------------------- 7. contraste con el CSV
sep("7. CONTRASTE CON estaciones_CTD_con_ZONA_MACROFAUNA.csv")
d = pd.read_csv(CSV)
cz = d.zona_mf.dropna().astype(str).str.strip().value_counts().sort_index()
gz = g.zona_mf.astype(str).str.strip().unique()
print("zonas únicas en CSV :", len(cz), sorted(cz.index.tolist()))
print("zonas únicas en GPKG:", len(gz), sorted(gz.tolist()))
print("\nen CSV y no en GPKG:", sorted(set(cz.index) - set(gz)))
print("en GPKG y no en CSV:", sorted(set(gz) - set(cz.index)))
print("\nn estaciones por zona (CSV):")
print(cz.to_string())
# estaciones dentro de su polígono? (vectorizado, una sola reproyección)
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
st_m = st.to_crs(CRS_ALBERS)

zonas_u = ga[["zona_mf", "geometry"]].copy()
zonas_u["zona_key"] = zonas_u.zona_mf.astype(str).str.strip()
un_geom = unary_union(list(ga.geometry))

parts = zonas_u.sindex  # STRtree sobre zonas
inside_own, dist_own = [], []
for i, r in st_m.iterrows():
    key = str(r.zona_mf).strip()
    own = zonas_u.loc[zonas_u.zona_key == key, "geometry"]
    if len(own) == 0:
        inside_own.append(None); dist_own.append(None); continue
    og = own.iloc[0]
    pt = r.geometry
    inside_own.append(bool(shapely.contains(og, pt)))
    dist_own.append(float(shapely.boundary(og).distance(pt)) if not og.geom_type == "MultiPolygon"
                     else float(shapely.boundary(og).distance(pt)))

st["dentro_su_zona"] = inside_own
st["dentro_alguna_zona"] = [bool(shapely.contains(un_geom, p)) for p in st_m.geometry]
st["dist_borde_km"] = pd.Series(dist_own, dtype=float) / 1000.0
print(f"\nestaciones DENTRO de su propia zona: {int(st.dentro_su_zona.fillna(False).sum())}/{len(st)}")
print(f"estaciones DENTRO de alguna zona   : {int(st.dentro_alguna_zona.sum())}/{len(st)}")
fuera = st[~st.dentro_su_zona.fillna(False)]
if len(fuera):
    print("\nestaciones fuera de su zona (top 15 por distancia al borde):")
    print(fuera.nlargest(15, "dist_borde_km")[["archivo", "estacion_id", "zona_mf", "dist_borde_km"]]
          .to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
    print("resumen por zona de estaciones fuera:")
    print(fuera.groupby("zona_mf").size().to_string())

# ------------------------------------------------------------ 8. export
sep("8. EXPORTACIÓN DE RESULTADOS (solo auditoría)")
res.to_csv(f"{OUT}/areas_por_zona.csv", index=False)
ext.to_csv(f"{OUT}/partes_extension_por_zona.csv", index=False)
tbl.to_csv(f"{OUT}/integridad_tierra_por_zona.csv", index=False)
st.drop(columns="geometry").to_csv(f"{OUT}/estaciones_dentro_zona.csv", index=False)
print("escrito en", OUT)
print("GPKG NO fue modificado (lectura con pyogrio).")
