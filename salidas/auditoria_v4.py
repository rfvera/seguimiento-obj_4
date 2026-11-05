#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auditoría v4 (SOLO LECTURA) de zonas_macrofauna.gpkg regenerado con la regla
topológica: se conservan las partes conectadas por mar a una parte ancla
(componente conexa de la máscara marina); se descartan las de otra componente.

Comprueba: inventario, áreas, Puyuhuapi, partes sin estación y su componente
marina, partes < 1 km², distancia estricta geodésica, tierra residual con/sin
set_precision, solapamiento, md5. NO escribe en el GPKG.
"""
import sys, os, hashlib
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.ops import unary_union, nearest_points
from shapely.geometry import box
from pyproj import CRS, Geod
from scipy.spatial import cKDTree
import pyproj, pyogrio

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
GPKG = f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg"
LAYER = "zonas_macrofauna"
COUNTRIES = f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp"
CSV = f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv"
OUT = f"{BASE}/salidas/auditoria_v4"
os.makedirs(OUT, exist_ok=True)

TOL_KM2 = 0.001
GRID = 1e-9
ALB = CRS.from_user_input("ESRI:102033")
UTM = CRS.from_user_input("EPSG:32719")
GEOD = Geod(ellps="WGS84")

def sep(t):
    print("\n" + "=" * 84); print(t); print("=" * 84)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def solo_poligonos(g):
    if g is None or g.is_empty:
        return None
    partes = []
    for p in (g.geoms if g.geom_type.startswith("Multi") or g.geom_type == "GeometryCollection" else [g]):
        if p.geom_type == "Polygon":
            partes.append(p)
        elif p.geom_type == "GeometryCollection":
            partes.extend([q for q in p.geoms if q.geom_type == "Polygon"])
    return unary_union(partes) if partes else None

def area_alb(geom4326):
    if geom4326 is None or geom4326.is_empty:
        return 0.0
    return gpd.GeoSeries([shapely.segmentize(geom4326, 0.005)], crs=4326
                         ).to_crs(ALB).iloc[0].area / 1e6

def area_geod(geom4326):
    return abs(GEOD.geometry_area_perimeter(geom4326)[0]) / 1e6

def dist_geod(pt4326, geom4326):
    q = nearest_points(pt4326, geom4326)[1]
    return GEOD.inv(pt4326.x, pt4326.y, q.x, q.y)[2]

# ------------------------------------------------------------------ 0
sep("0. ENTORNO Y HUELLA (antes de leer)")
MD5_INI = md5(GPKG)
print("python    :", sys.version.split()[0])
print("geopandas :", gpd.__version__, "| shapely:", shapely.__version__,
      "| pyproj:", pyproj.__version__, "| pyogrio:", pyogrio.__version__,
      "| GDAL:", pyogrio.__gdal_version_string__)
print("md5 INICIAL:", MD5_INI)
print("mtime_ns / size:", os.stat(GPKG).st_mtime_ns, os.path.getsize(GPKG))

# ------------------------------------------------------------------ 1
sep("1. INVENTARIO, CRS, VALIDEZ, VACÍAS")
g = gpd.read_file(GPKG, layer=LAYER, engine="pyogrio")
print("features           :", len(g))
print("columnas           :", list(g.columns))
print("zonas únicas       :", g.zona_mf.nunique(), "| duplicadas:", int(len(g) - g.zona_mf.nunique()))
print("tipos de geometría :", g.geom_type.value_counts().to_dict())
print("CRS                :", g.crs.to_string(), "| EPSG:", g.crs.to_epsg(),
      "| geográfico:", g.crs.is_geographic)
print("bounds             :", [round(v, 6) for v in g.total_bounds])
print("is_valid           :", int(g.geometry.is_valid.sum()), "/", len(g))
print("is_empty           :", int(g.geometry.is_empty.sum()))
print("is_null            :", int(g.geometry.isna().sum()))
print("motivos invalidez   :", pd.Series(shapely.is_valid_reason(list(g.geometry.values))).value_counts().to_dict())
print("make_valid cambia  :", bool((shapely.get_type_id(list(g.geometry.values)) !=
      shapely.get_type_id(list(shapely.make_valid(list(g.geometry.values))))).any()))

d = pd.read_csv(CSV)
st = gpd.GeoDataFrame(d, geometry=gpd.points_from_xy(d.lon, d.lat), crs=4326)
print("\nzonas CSV:", st.zona_mf.nunique(), "| estaciones:", len(st),
      "| zonas GPKG == CSV:", set(st.zona_mf.str.strip()) == set(g.zona_mf.str.strip()))

# ------------------------------------------------------------------ 2
sep("2. ÁREA TOTAL Y POR ZONA")
rows = []
for i, r in g.iterrows():
    n = len(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else 1
    rows.append({"zona_mf": r.zona_mf, "n_partes": n,
                 "albers_km2": area_alb(r.geometry),
                 "geodesica_km2": area_geod(r.geometry),
                 "epsg6933_km2": gpd.GeoSeries([r.geometry], crs=4326).to_crs(6933).iloc[0].area / 1e6})
A = pd.DataFrame(rows).sort_values("albers_km2", ascending=False)
print(A.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\nTOTAL Albers (densificado): {A.albers_km2.sum():,.4f} km²")
print(f"TOTAL geodésico           : {A.geodesica_km2.sum():,.4f} km²")
print(f"TOTAL EPSG:6933           : {A.epsg6933_km2.sum():,.4f} km²")
print(f"desvío Albers vs geodésica: {(A.albers_km2.sum()-A.geodesica_km2.sum())/A.geodesica_km2.sum()*100:+.4f}%")
print(f"total de partes           : {int(A.n_partes.sum())} | zonas con >1 parte: {int((A.n_partes>1).sum())}")

# ------------------------------------------------------------------ 3
sep("3. PUYUHUPI")
pi = g.index[g.zona_mf == "Puyuhuapi"][0]
puy = g.geometry.iloc[pi]
pp = list(puy.geoms) if puy.geom_type == "MultiPolygon" else [puy]
print(f"partes: {len(pp)}")
for k, p in enumerate(sorted(pp, key=lambda x: -x.area)):
    print(f"  parte {k}: {area_alb(p):,.4f} km² (Albers) | {area_geod(p):,.4f} km² (geod) | "
          f"huecos {len(p.interiors)} | bbox {[round(v,6) for v in p.bounds]}")
print(f"área total : {A.loc[A.zona_mf=='Puyuhuapi','albers_km2'].iloc[0]:,.4f} km² (Albers) / "
      f"{A.loc[A.zona_mf=='Puyuhuapi','geodesica_km2'].iloc[0]:,.4f} km² (geodésica)")
print(f"bbox total : {[round(v,6) for v in puy.bounds]}")
print(f"fragmento atlántico 11.009,99 km²: "
      f"{'PRESENTE' if any(abs(area_alb(p)-11009.99) < 1.0 for p in pp) else 'AUSENTE'}")
print(f"¿alguna parte con lon_max > -70? {'SÍ' if any(p.bounds[2] > -70 for p in pp) else 'NO'}")
sp = st[st.zona_mf.str.strip() == "Puyuhuapi"]
dentro = [shapely.covers(puy, q) for q in sp.geometry]
dd = [dist_geod(q, puy) for q in sp.geometry]
print(f"estaciones: {len(sp)} | dentro {int(sum(dentro))} | fuera {int(len(sp)-sum(dentro))}")
print(f"distancia estación -> polígono: min {min(dd)/1e3:,.3f} km | MAX {max(dd)/1e3:,.3f} km | media {np.mean(dd)/1e3:,.3f} km")
print("  estaciones fuera:", [(sp.estacion_id.iloc[i], round(dd[i]/1e3, 3)) for i, x in enumerate(dentro) if not x])

# ------------------------------------------------------------------ 4
sep("4. PARTES SIN ESTACIÓN CONSERVADAS Y SU COMPONENTE MARINA")
# --- reconstrucción de la máscara marina igual que el generador
coords = np.array([(p.x, p.y) for p in st.geometry])
xmin, ymin = coords.min(axis=0); xmax, ymax = coords.max(axis=0)
frame = box(xmin - 0.5, ymin - 0.5, xmax + 0.5, ymax + 0.5)
c = gpd.read_file(COUNTRIES, engine="pyogrio")
paises = c[c.geometry.intersects(frame)].copy()
tierra = shapely.make_valid(unary_union([shapely.make_valid(x) for x in paises.geometry]))
marino = solo_poligonos(shapely.make_valid(frame.difference(tierra)))
comps = list(marino.geoms) if marino.geom_type == "MultiPolygon" else [marino]
comp_areas = np.array([area_alb(x) for x in comps])
print(f"marco (bbox estaciones ±0,5°) : {[round(v,6) for v in frame.bounds]}")
print(f"países restados               : {paises.ADMIN.tolist()}")
print(f"componentes conexas de la máscara marina: {len(comps)}")
print(f"  área de la mayor: {comp_areas.max():,.1f} km² | de la 2ª: {np.sort(comp_areas)[-2]:,.3f} km² | "
      f"mediana {np.median(comp_areas):,.6f} km²")
mayor = int(np.argmax(comp_areas))
print(f"  componentes > 1 km²: {int((comp_areas>1).sum())} | > 100 km²: {int((comp_areas>100).sum())}")

# --- asignación de cada parte a su componente
def comp_de(parte):
    rp = parte.representative_point()
    hits = [k for k, cc in enumerate(comps) if cc.contains(rp) or cc.covers(rp)]
    if hits:
        return hits[0] if len(hits) == 1 else -1, len(hits)
    hit2 = [k for k, cc in enumerate(comps) if cc.intersects(parte)]
    return (hit2[0] if len(hit2) == 1 else -2), len(hit2)

PR = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    pts = st[st.zona_mf.str.strip() == key]
    ps = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
    anclas = [p for p in ps if any(shapely.covers(p, q) for q in pts.geometry)]
    for k, p in enumerate(sorted(ps, key=lambda x: -x.area)):
        cid, nh = comp_de(p)
        es_ancla = any(p.equals(a) for a in anclas)
        # ¿esa componente contiene algún ancla de la zona?
        comp_tiene_ancla = None
        if cid >= 0:
            comp_tiene_ancla = any(comps[cid].contains(a.representative_point()) or
                                   comps[cid].covers(a.representative_point()) or
                                   comps[cid].intersects(a) for a in anclas)
        PR.append({"zona_mf": key, "parte": k, "area_km2": area_alb(p),
                   "n_est_dentro": sum(1 for q in pts.geometry if shapely.covers(p, q)),
                   "es_ancla": es_ancla, "componente": cid, "n_comps_hit": nh,
                   "comp_tiene_ancla": comp_tiene_ancla,
                   "n_huecos": len(p.interiors),
                   "lon_min": p.bounds[0], "lat_min": p.bounds[1],
                   "lon_max": p.bounds[2], "lat_max": p.bounds[3]})
P = pd.DataFrame(PR)
sin_est = P[P.n_est_dentro == 0]
print(f"\ntotal partes: {len(P)} | con estación (ancla): {int(P.es_ancla.sum())} | "
      f"SIN estación: {len(sin_est)}")
print(f"PARTES SIN ESTACIÓN EN COMPONENTE SIN ANCLA: "
      f"{int((sin_est.comp_tiene_ancla == False).sum())}  "
      f"{'OK' if int((sin_est.comp_tiene_ancla == False).sum()) == 0 else '<-- REVISAR'}")
print(f"partes sin estación en la componente mayor (id {mayor}): "
      f"{int((sin_est.componente == mayor).sum())} de {len(sin_est)}")
print(f"partes con asignación ambigua de componente (n_comps_hit != 1): "
      f"{int((P.n_comps_hit != 1).sum())}")
if len(sin_est):
    print("\npartes SIN estación conservadas:")
    print(sin_est[["zona_mf", "parte", "area_km2", "componente", "comp_tiene_ancla",
                   "n_huecos", "lon_min", "lat_min", "lon_max", "lat_max"]]
          .to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print("\ncomponentes usadas por zona (>1 componente => zona anclada en varias):")
byz = P[P.es_ancla].groupby("zona_mf").componente.agg(lambda s: sorted(set(s)))
for z, cs in byz.items():
    if len(cs) > 1:
        print(f"  {z}: componentes {cs}")
small = P[P.area_km2 < 1.0].sort_values("area_km2")
print(f"\nPARTES MENORES A 1 km²: {len(small)} (suma {small.area_km2.sum():,.6f} km²)")
if len(small):
    print(small[["zona_mf", "parte", "area_km2", "n_est_dentro", "componente",
                 "lon_min", "lat_min", "lon_max", "lat_max"]].to_string(
          index=False, float_format=lambda v: f"{v:,.6f}"))
print(f"partes menores a 0,001 km²: {int((P.area_km2 < TOL_KM2).sum())}")

# ------------------------------------------------------------------ 5
sep("5. DISTANCIA ESTRICTA GEODÉSICA (punto de cada parte más alejado de toda estación de su zona)")
rows = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    pts = st[st.zona_mf.str.strip() == key]
    pm = pts.to_crs(UTM); S = np.column_stack([pm.geometry.x.values, pm.geometry.y.values])
    tree = cKDTree(S); Sll = np.column_stack([pts.lon.values, pts.lat.values])
    best = 0.0; arg = None
    for p in (r.geometry.geoms if r.geometry.geom_type == "MultiPolygon" else [r.geometry]):
        C = shapely.get_coordinates(shapely.segmentize(p, 0.0002))   # ~22 m
        minx, miny, maxx, maxy = p.bounds
        gx, gy = np.meshgrid(np.arange(minx, maxx, 0.01), np.arange(miny, maxy, 0.01))
        cand = np.column_stack([gx.ravel(), gy.ravel()])
        C = np.vstack([C, cand[shapely.contains_xy(p, cand[:, 0], cand[:, 1])]])
        Cm = gpd.GeoSeries(gpd.points_from_xy(C[:, 0], C[:, 1]), crs=4326).to_crs(UTM)
        Cu = np.column_stack([Cm.geometry.x.values, Cm.geometry.y.values])
        _, idx = tree.query(Cu)
        _, _, dist = GEOD.inv(C[:, 0], C[:, 1], Sll[idx][:, 0], Sll[idx][:, 1])
        j = int(np.argmax(dist))
        if dist[j] > best:
            best = dist[j]; arg = (round(C[j, 0], 5), round(C[j, 1], 5))
    rows.append({"zona_mf": key, "n_est": len(pts), "dist_max_km": best / 1e3,
                 "exceso_m": best - 100000.0,
                 "lon_argmax": arg[0], "lat_argmax": arg[1]})
D = pd.DataFrame(rows).sort_values("dist_max_km", ascending=False)
print(D.to_string(index=False, float_format=lambda v: f"{v:,.6f}"))
print(f"\nmáximo global: {D.dist_max_km.max():,.6f} km ({D.loc[D.dist_max_km.idxmax(),'zona_mf']})")
print(f"zonas que exceden 100 km: {D.loc[D.dist_max_km>100,'zona_mf'].tolist() or 'ninguna'}")
print(f"exceso máximo sobre 100 km: {D.exceso_m.max():+,.6f} m")
print("zonas entre 95 y 100 km (margen < 5 km):")
print(D[(D.dist_max_km > 95) & (D.dist_max_km <= 100)][["zona_mf", "dist_max_km"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.4f}"))

# ------------------------------------------------------------------ 6
sep("6. TIERRA RESIDUAL CON/SIN set_precision(1e-9) Y SOLAPAMIENTO")
land = tierra
land_g = shapely.set_precision(tierra, GRID)
rows = []
for i, r in g.iterrows():
    ii = shapely.intersection(r.geometry, land)
    ig = shapely.intersection(shapely.set_precision(r.geometry, GRID), land_g)
    rows.append({"zona_mf": r.zona_mf, "sin_rejilla_km2": area_alb(ii),
                 "con_rejilla_km2": area_alb(ig),
                 "n_piezas": (len(ii.geoms) if hasattr(ii, "geoms") else (0 if ii.is_empty else 1))})
T = pd.DataFrame(rows)
print(T.to_string(index=False, float_format=lambda v: f"{v:.3e}"))
print(f"\nTOTAL sin rejilla: {T.sin_rejilla_km2.sum():.6e} km² = {T.sin_rejilla_km2.sum()*1e6:.2f} m²")
print(f"TOTAL con rejilla: {T.con_rejilla_km2.sum():.6e} km² = {T.con_rejilla_km2.sum()*1e6:.6f} m²")
print(f"zonas con >= 0,001 km² de tierra: sin rejilla "
      f"{T.loc[T.sin_rejilla_km2>=TOL_KM2,'zona_mf'].tolist() or 'ninguna'} | con rejilla "
      f"{T.loc[T.con_rejilla_km2>=TOL_KM2,'zona_mf'].tolist() or 'ninguna'}")
print("\npor país:")
for adm in paises.ADMIN.unique():
    cp = shapely.make_valid(unary_union([shapely.make_valid(x) for x in paises.loc[paises.ADMIN == adm, "geometry"]]))
    ts = tg = 0.0
    for i, r in g.iterrows():
        ii = shapely.intersection(r.geometry, cp)
        if not ii.is_empty: ts += area_alb(ii)
        ig = shapely.intersection(shapely.set_precision(r.geometry, GRID), shapely.set_precision(cp, GRID))
        if not ig.is_empty: tg += area_alb(ig)
    print(f"  {adm:<34} sin {ts:.6e} km² | con {tg:.6e} km²")

GDf = g.copy(); GDf["geometry"] = [shapely.segmentize(x, 0.005) for x in g.geometry]
ga = GDf.to_crs(ALB)
suma = ga.area.sum() / 1e6; u = unary_union(list(ga.geometry))
print(f"\nSOLAPAMIENTO: suma {suma:,.6f} km² | unión {u.area/1e6:,.6f} km² | "
      f"solape {suma-u.area/1e6:,.6f} km² ({(suma-u.area/1e6)*1e6:,.1f} m²)")
pairs = [(g.zona_mf.iloc[i], g.zona_mf.iloc[j],
          shapely.intersection(ga.geometry.iloc[i], ga.geometry.iloc[j]).area / 1e6)
         for i in range(len(ga)) for j in range(i + 1, len(ga))
         if shapely.intersection(ga.geometry.iloc[i], ga.geometry.iloc[j]).area / 1e6 > TOL_KM2]
print(f"pares con solape > 0,001 km²: {len(pairs)}")
for p in sorted(pairs, key=lambda t: -t[2]):
    print(f"  {p[0]} ∩ {p[1]} = {p[2]:,.6f} km²")

# ------------------------------------------------------------------ 7
sep("7. EXPORTACIÓN Y HUELLA FINAL")
A.to_csv(f"{OUT}/areas_v4.csv", index=False)
P.to_csv(f"{OUT}/partes_v4.csv", index=False)
D.to_csv(f"{OUT}/distancias_v4.csv", index=False)
T.to_csv(f"{OUT}/tierra_v4.csv", index=False)
print("csv en", OUT)
MD5_FIN = md5(GPKG)
print("md5 INICIAL:", MD5_INI)
print("md5 FINAL  :", MD5_FIN)
print("¿CAMBIÓ?   :", "NO (intacto)" if MD5_FIN == MD5_INI else "SÍ -- ALERTA")
