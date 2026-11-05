#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auditoría v2 (solo lectura) de zonas_macrofauna.gpkg regenerado con:
  - recorte por unión de buffers de 100 km alrededor de las estaciones propias
  - resta de tierra con set_precision(1e-9)

Comprueba: inventario, validez, Puyuhuapi, tierra residual con y sin rejilla de
precisión, solapamiento, distancia máxima polígono->estación propia (<=100 km),
partes < 1 km².
NO escribe en el GPKG.
"""
import sys, os, json, hashlib
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.ops import unary_union
from pyproj import CRS, Geod
import pyproj, pyogrio

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
GPKG = f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg"
LAYER = "zonas_macrofauna"
COUNTRIES = f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp"
CSV = f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv"
OUT = f"{BASE}/salidas/auditoria_v2"
os.makedirs(OUT, exist_ok=True)

TOL_KM2 = 0.001
GRID = 1e-9
ALB = CRS.from_user_input("ESRI:102033")

def sep(t):
    print("\n" + "=" * 80); print(t); print("=" * 80)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

sep("0. ENTORNO Y HUELLA DEL ARCHIVO (antes de leer)")
MD5_INI = md5(GPKG)
print("python    :", sys.version.split()[0])
print("geopandas :", gpd.__version__, "| shapely:", shapely.__version__,
      "| pyproj:", pyproj.__version__, "| pyogrio:", pyogrio.__version__)
print("GDAL      :", pyogrio.__gdal_version_string__)
print("md5 INICIAL:", MD5_INI)
print("mtime/size :", os.stat(GPKG).st_mtime_ns, os.path.getsize(GPKG))

# ---------------------------------------------------------------- 1. lectura
sep("1. INVENTARIO, CRS, VALIDEZ, VACÍAS")
g = gpd.read_file(GPKG, layer=LAYER, engine="pyogrio")
print("features          :", len(g))
print("columnas          :", list(g.columns))
print("zonas únicas      :", g.zona_mf.nunique(), "| duplicadas:",
      int(len(g) - g.zona_mf.nunique()))
print("tipos geometría   :", g.geom_type.value_counts().to_dict())
print("CRS               :", g.crs.to_string(), "| EPSG:", g.crs.to_epsg(),
      "| geográfico:", g.crs.is_geographic)
print("bounds            :", [round(v, 6) for v in g.total_bounds])
print("is_valid          :", int(g.geometry.is_valid.sum()), "/", len(g))
print("is_empty          :", int(g.geometry.is_empty.sum()))
print("is_null           :", int(g.geometry.isna().sum()))
print("geom no vacías y válidas:", int((g.geometry.is_valid & ~g.geometry.is_empty).sum()))
rev = shapely.is_valid_reason(list(g.geometry.values))
print("motivos de invalidez:", pd.Series(rev).value_counts().to_dict())
print("¿make_valid cambia algo?:",
      bool(len(np.unique(rev)) > 1 or (shapely.get_type_id(list(g.geometry.values)) !=
           shapely.get_type_id(list(shapely.make_valid(list(g.geometry.values))))).any()))

ga = g.to_crs(ALB)  # métrico, área equivalente (vértices originales)
# Reproyección correcta para áreas: densificar el borde en 4326 (~500 m) ANTES de
# proyectar, porque un segmento recto en lon/lat no es recto en Albers.
GD = g.copy()
GD["geometry"] = [shapely.segmentize(x, 0.005) for x in g.geometry]
gad = GD.to_crs(ALB)
print("área total sin densificar la reproyección: %.4f km²" % (ga.area.sum() / 1e6))
print("área total densificada (valor correcto)  : %.4f km²" % (gad.area.sum() / 1e6))
ga = gad

sep("2. PUYUHAPI: ¿DESAPARECIÓ EL FRAGMENTO ATLÁNTICO?")
puy_i = g.index[g.zona_mf == "Puyuhuapi"][0]
puy = g.geometry.iloc[puy_i]
parts = list(puy.geoms) if puy.geom_type == "MultiPolygon" else [puy]
info = []
for k, p in enumerate(parts):
    pm = gpd.GeoSeries([shapely.segmentize(p, 0.005)], crs=4326).to_crs(ALB).iloc[0]
    info.append({"parte": k, "area_km2": pm.area / 1e6, "lon_min": round(p.bounds[0], 4),
                 "lat_min": round(p.bounds[1], 4), "lon_max": round(p.bounds[2], 4),
                 "lat_max": round(p.bounds[3], 4),
                 "n_huecos": len(p.interiors), "n_vert": len(p.exterior.coords)})
PI = pd.DataFrame(info).sort_values("area_km2", ascending=False)
print(f"Puyuhuapi: {len(parts)} partes")
print(PI.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
a_puy = ga.geometry.loc[puy_i].area / 1e6
print(f"\nárea total Puyuhuapi AHORA : {a_puy:,.4f} km²   (antes: 11,667.9419 km²)")
print(f"bbox                       : {[round(v,6) for v in puy.bounds]}")
print(f"fragmento de 11,009.99 km² presente? "
      f"{'SÍ' if any(abs(x['area_km2']-11009.99) < 1.0 for x in info) else 'NO'}")

d = pd.read_csv(CSV)
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
dpu = st[st.zona_mf.str.strip() == "Puyuhuapi"].to_crs(ALB)
pm = ga.geometry.loc[puy_i]
dmin = [shapely.distance(pm, p) for p in dpu.geometry]
print(f"\nestaciones Puyuhuapi: {len(dpu)}")
print(f"  distancia polígono-estación: min {min(dmin)/1e3:,.3f} km | MAX {max(dmin)/1e3:,.3f} km")
print(f"  estaciones DENTRO: {sum(shapely.contains(pm, p) for p in dpu.geometry)}/{len(dpu)}")
print(f"  estaciones en la parte mayor (si >1): "
      f"{sum(shapely.contains(gpd.GeoSeries([parts[0]], crs=4326).to_crs(ALB).iloc[0], p) for p in dpu.geometry)}")

# ------------------------------------------------- 3. tierra residual
sep("3. TIERRA RESIDUAL: CON Y SIN REJILLA set_precision(1e-9)")
c = gpd.read_file(COUNTRIES, engine="pyogrio")
bb = shapely.box(*g.total_bounds).buffer(0.5)
sel = c[c.geometry.intersects(bb)].copy()
print("países/entidades que intersectan bbox+0,5°:", sel.ADMIN.tolist())
land4326 = shapely.make_valid(unary_union([shapely.make_valid(x) for x in sel.geometry]))
print("unión 4326 válida:", land4326.is_valid, "| vacía:", land4326.is_empty)
land_g = shapely.set_precision(land4326, GRID)
land_m = shapely.make_valid(gpd.GeoSeries([land4326], crs=4326).to_crs(ALB).iloc[0])
land_gm = shapely.make_valid(gpd.GeoSeries([land_g], crs=4326).to_crs(ALB).iloc[0])

rows = []
for i, r in g.iterrows():
    z4326 = r.geometry
    zg4326 = shapely.set_precision(z4326, GRID)
    # sin rejilla (intersección en 4326; el resultado se densifica antes de proyectar)
    i_plain = shapely.intersection(z4326, land4326)
    a_plain = (gpd.GeoSeries([shapely.segmentize(i_plain, 0.005)], crs=4326)
               .to_crs(ALB).iloc[0].area / 1e6 if not i_plain.is_empty else 0.0)
    # con rejilla
    i_grid = shapely.intersection(zg4326, land_g)
    a_grid = (gpd.GeoSeries([shapely.segmentize(i_grid, 0.005)], crs=4326)
              .to_crs(ALB).iloc[0].area / 1e6 if not i_grid.is_empty else 0.0)
    # nº de piezas de la intersección (astillas)
    n_pzas = 0
    if not i_plain.is_empty:
        n_pzas = len(i_plain.geoms) if i_plain.geom_type.startswith("Multi") else 1
    rows.append({"zona_mf": r.zona_mf, "area_km2": ga.geometry.loc[i].area / 1e6,
                 "area_6933_km2": gpd.GeoSeries([r.geometry], crs=4326).to_crs(6933).iloc[0].area / 1e6,
                 "tierra_sin_rejilla": a_plain, "tierra_con_rejilla": a_grid,
                 "n_piezas": n_pzas})
TI = pd.DataFrame(rows)
raw_sin = TI.tierra_sin_rejilla.sum(); raw_con = TI.tierra_con_rejilla.sum()
for col in ["tierra_sin_rejilla", "tierra_con_rejilla"]:
    TI[col] = TI[col].mask(TI[col].abs() < TOL_KM2, 0.0)
TI["delta"] = TI.tierra_sin_rejilla - TI.tierra_con_rejilla
print("\n(se aplica el criterio <0,001 km² = 0 después de medir y de calcular los totales crudos)")
print(f"TOTALES CRUDOS: sin rejilla {raw_sin:,.9f} km² | con rejilla {raw_con:,.9f} km²")
print(TI.to_string(index=False, float_format=lambda v: f"{v:,.6f}"))
print(f"\nSYN rejilla : {raw_sin:,.9f} km² (crudo) | enmascarado: {TI.tierra_sin_rejilla.sum():,.6f} km²")
print(f"CON rejilla : {raw_con:,.9f} km² (crudo) | enmascarado: {TI.tierra_con_rejilla.sum():,.6f} km²")
print(f"diferencia  : {raw_sin - raw_con:,.9f} km²")
print(f"zonas con tierra >= 0,001 km² sin rejilla: "
      f"{TI.loc[TI.tierra_sin_rejilla>=TOL_KM2,'zona_mf'].tolist()}")
print(f"zonas con tierra >= 0,001 km² con rejilla: "
      f"{TI.loc[TI.tierra_con_rejilla>=TOL_KM2,'zona_mf'].tolist()}")
print(f"\nárea total de las zonas (Albers densificado): {TI.area_km2.sum():,.4f} km²")
print(f"área total de las zonas (EPSG:6933, el CRS del generador): "
      f"{TI.area_6933_km2.sum():,.4f} km²  (AGENTS.md documenta 177,266.48 km²)")

# por país (se intersecta en 4326 -- CRS fuente -- y se proyecta el resultado)
print("\ntierra por país (intersección en 4326, como en la tabla anterior):")
for adm in sel.ADMIN.unique():
    cp = shapely.make_valid(unary_union([shapely.make_valid(x)
                                         for x in sel.loc[sel.ADMIN == adm, "geometry"]]))
    tot = totg = 0.0
    for i, r in g.iterrows():
        inter = shapely.intersection(r.geometry, cp)
        if not inter.is_empty:
            tot += gpd.GeoSeries([shapely.segmentize(inter, 0.005)], crs=4326
                                 ).to_crs(ALB).iloc[0].area / 1e6
        interg = shapely.intersection(shapely.set_precision(r.geometry, GRID),
                                      shapely.set_precision(cp, GRID))
        if not interg.is_empty:
            totg += gpd.GeoSeries([shapely.segmentize(interg, 0.005)], crs=4326
                                  ).to_crs(ALB).iloc[0].area / 1e6
    print(f"  {adm:<34} sin rejilla {tot:,.6f} km² | con rejilla {totg:,.6f} km²")

# ------------------------------------------------- 4. solapamiento
sep("4. SOLAPAMIENTO ENTRE ZONAS")
u = unary_union(list(ga.geometry))
suma = TI.area_km2.sum()
print(f"suma de áreas : {suma:,.4f} km²")
print(f"área de unión : {u.area/1e6:,.4f} km²")
print(f"solapamiento  : {suma - u.area/1e6:,.6f} km²")
pairs = []
for i in range(len(ga)):
    for j in range(i + 1, len(ga)):
        a = shapely.intersection(ga.geometry.iloc[i], ga.geometry.iloc[j]).area / 1e6
        if a > TOL_KM2:
            pairs.append((g.zona_mf.iloc[i], g.zona_mf.iloc[j], a))
pairs.sort(key=lambda t: -t[2])
print(f"pares con solape > 0,001 km²: {len(pairs)}")
for p in pairs[:20]:
    print(f"  {p[0]:<16} ∩ {p[1]:<16} = {p[2]:,.4f} km²")

# --------------------------------- 5. distancia máxima polígono->estación propia
sep("5. DISTANCIA MÁXIMA DE CADA ZONA A SU ESTACIÓN MÁS CERCANA (límite 100 km)")
print("Distancias GEODÉSICAS (pyproj.Geod, elipsoide WGS84), no proyectadas:")
print("ni Albers ni EPSG:6933 miden distancias correctamente a esta latitud.\n")
geod = Geod(ellps="WGS84")
zonas_u = g.zona_mf.astype(str).str.strip()
rows = []
stm_utm = st.to_crs(CRS.from_user_input("EPSG:32719"))
S_utm = np.column_stack([stm_utm.geometry.x.values, stm_utm.geometry.y.values])
S_ll = np.column_stack([st.lon.values, st.lat.values])
labels_all = st.zona_mf.astype(str).str.strip().values
from scipy.spatial import cKDTree
tree_all = cKDTree(S_utm)
for i, r in g.iterrows():
    key = zonas_u.iloc[i]
    sub = st[st.zona_mf.astype(str).str.strip() == key]
    if len(sub) == 0:
        rows.append({"zona_mf": key, "n_est": 0}); continue
    own = labels_all == key
    tree_own = cKDTree(S_utm[own])
    # muestreo: borde densificado 0.0005° (~55 m) + malla interior 0.02° (~2 km)
    P = shapely.get_coordinates(shapely.segmentize(r.geometry, 0.0005))
    minx, miny, maxx, maxy = r.geometry.bounds
    gx, gy = np.meshgrid(np.arange(minx, maxx, 0.02), np.arange(miny, maxy, 0.02))
    cand = np.column_stack([gx.ravel(), gy.ravel()])
    P = np.vstack([P, cand[shapely.contains_xy(r.geometry, cand[:, 0], cand[:, 1])]])
    Pm = gpd.GeoSeries(gpd.points_from_xy(P[:, 0], P[:, 1]), crs=4326).to_crs(
        CRS.from_user_input("EPSG:32719"))
    Pu = np.column_stack([Pm.geometry.x.values, Pm.geometry.y.values])
    # vecino más cercano por KD-tree en UTM; distancia final GEODÉSICA
    _, idx = tree_own.query(Pu)
    _, _, dist = geod.inv(P[:, 0], P[:, 1], S_ll[own][idx][:, 0], S_ll[own][idx][:, 1])
    j = int(np.argmax(dist))
    _, idxg = tree_all.query(Pu[[j]])
    _, _, distg = geod.inv(P[j, 0], P[j, 1], S_ll[idxg[0], 0], S_ll[idxg[0], 1])
    rows.append({"zona_mf": key, "n_est": len(sub),
                 "dist_max_km": dist.max() / 1e3,
                 "margen_km": 100 - dist.max() / 1e3,
                 "lon_arg": round(P[j, 0], 4), "lat_arg": round(P[j, 1], 4),
                 "est_cercana_global": st.estacion_id.iloc[idxg[0]],
                 "zona_est_global": labels_all[idxg[0]],
                 "dist_global_km": distg / 1e3,
                 "n_muestras": len(P)})
D = pd.DataFrame(rows).sort_values("dist_max_km", ascending=False)
D["cumple_100km"] = D.dist_max_km <= 100.0
print(D.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
print(f"\nmáximo GLOBAL: {D.dist_max_km.max():,.3f} km "
      f"({D.loc[D.dist_max_km.idxmax(),'zona_mf']}) | mínimo: {D.dist_max_km.min():,.3f} km")
print(f"zonas que exceden 100 km: {D.loc[~D.cumple_100km,'zona_mf'].tolist() or 'ninguna'}")
print("zonas más cerca del límite (margen < 10 km):")
print(D[D.margen_km < 10][["zona_mf", "dist_max_km", "margen_km"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.3f}"))

# --------------------------------- 6. partes y geometrías
sep("6. PARTES, HUECOS Y PARTES MENORES A 1 km²")
rows = []
for i, r in g.iterrows():
    parts = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
    for k, p in enumerate(parts):
        pm = gpd.GeoSeries([shapely.segmentize(p, 0.005)], crs=4326).to_crs(ALB).iloc[0]
        rows.append({"zona_mf": r.zona_mf, "parte": k, "area_km2": pm.area / 1e6,
                     "n_huecos": len(p.interiors),
                     "lon_min": p.bounds[0], "lat_min": p.bounds[1],
                     "lon_max": p.bounds[2], "lat_max": p.bounds[3]})
P = pd.DataFrame(rows)
print(f"total partes: {len(P)} | zonas con >1 parte: "
      f"{int((P.groupby('zona_mf').size()>1).sum())} | huecos: {int(P.n_huecos.sum())}")
print("\npartes por zona:")
print(P.groupby("zona_mf").agg(n_partes=("area_km2", "size"),
                               area_total=("area_km2", "sum"),
                               huecos=("n_huecos", "sum")).to_string(
      float_format=lambda v: f"{v:,.4f}"))
small = P[P.area_km2 < 1.0].sort_values("area_km2")
print(f"\nPARTES MENORES A 1 km²: {len(small)}  (área sumada {small.area_km2.sum():,.6f} km²)")
if len(small):
    print(small.to_string(index=False, float_format=lambda v: f"{v:,.6f}"))
print(f"\npartes menores a 0,001 km²: {int((P.area_km2 < TOL_KM2).sum())}")
menor = P.sort_values("area_km2").iloc[0]
print(f"parte menor: {menor.zona_mf} parte {int(menor.parte)} área {menor.area_km2:,.6f} km², "
      f"bbox {menor.lon_min:.4f},{menor.lat_min:.4f} a {menor.lon_max:.4f},{menor.lat_max:.4f}")

# verificación geodésica del área total
geod = Geod(ellps="WGS84")
geo = sum(abs(geod.geometry_area_perimeter(x)[0]) for x in g.geometry) / 1e6
print(f"\ncontrol geodésico del área total: {geo:,.4f} km² "
      f"(Albers {TI.area_km2.sum():,.4f}; desvío "
      f"{(TI.area_km2.sum()-geo)/geo*100:+.4f}%)")

# ------------------------------------------------- export + md5 final
sep("7. EXPORTACIÓN Y HUELLA FINAL")
TI.to_csv(f"{OUT}/tierra_residual.csv", index=False)
D.to_csv(f"{OUT}/distancia_estaciones.csv", index=False)
P.to_csv(f"{OUT}/partes.csv", index=False)
print("csv en", OUT)
MD5_FIN = md5(GPKG)
print("md5 INICIAL:", MD5_INI)
print("md5 FINAL  :", MD5_FIN)
print("¿CAMBIÓ?   :", "NO (intacto)" if MD5_FIN == MD5_INI else "SÍ -- ALERTA")
