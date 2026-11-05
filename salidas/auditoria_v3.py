#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auditoría v3 (SOLO LECTURA) de zonas_macrofauna.gpkg regenerado con:
  - búfer de 100 km GEODÉSICO (pyproj.Geod, 72 vértices) en lugar de EPSG:6933
  - conservación de solo las partes respaldadas por estaciones de la zona

Comprueba: inventario, áreas (Albers densificado / geodésica / 6933), Puyuhuapi,
partes sin estación, distancia geodésica parte->estación (dos criterios),
tierra residual con y sin set_precision, solapamiento, md5.
NO escribe en el GPKG.
"""
import sys, os, hashlib
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from shapely.ops import unary_union, nearest_points
from pyproj import CRS, Geod
from scipy.spatial import cKDTree
import pyproj, pyogrio

BASE = "/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4"
GPKG = f"{BASE}/salidas/figuras/zonas_macrofauna.gpkg"
LAYER = "zonas_macrofauna"
COUNTRIES = f"{BASE}/salidas/figuras/ne_10m_admin_0_countries.shp"
CSV = f"{BASE}/estaciones_CTD_con_ZONA_MACROFAUNA.csv"
OUT = f"{BASE}/salidas/auditoria_v3"
os.makedirs(OUT, exist_ok=True)

TOL_KM2 = 0.001
GRID = 1e-9
ALB = CRS.from_user_input("ESRI:102033")
UTM = CRS.from_user_input("EPSG:32719")
GEOD = Geod(ellps="WGS84")

def sep(t):
    print("\n" + "=" * 82); print(t); print("=" * 82)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def dens_area_km2(geom4326):
    """Área en km² en Albers, densificando antes de proyectar."""
    return gpd.GeoSeries([shapely.segmentize(geom4326, 0.005)], crs=4326
                         ).to_crs(ALB).iloc[0].area / 1e6

def geod_area_km2(geom4326):
    return abs(GEOD.geometry_area_perimeter(geom4326)[0]) / 1e6

def dist_geod_punto_geom(pt4326, geom4326):
    q = nearest_points(pt4326, geom4326)[1]
    return GEOD.inv(pt4326.x, pt4326.y, q.x, q.y)[2]

# ---------------------------------------------------------------- 0
sep("0. ENTORNO Y HUELLA (antes de leer)")
MD5_INI = md5(GPKG)
print("python    :", sys.version.split()[0])
print("geopandas :", gpd.__version__, "| shapely:", shapely.__version__,
      "| pyproj:", pyproj.__version__, "| pyogrio:", pyogrio.__version__,
      "| GDAL:", pyogrio.__gdal_version_string__)
print("md5 INICIAL:", MD5_INI)
print("mtime_ns/size:", os.stat(GPKG).st_mtime_ns, os.path.getsize(GPKG))
print("crs Albers, unidades:", ALB.axis_info[0].unit_name)

# ---------------------------------------------------------------- 1
sep("1. INVENTARIO, CRS, VALIDEZ, VACÍAS")
g = gpd.read_file(GPKG, layer=LAYER, engine="pyogrio")
print("features           :", len(g))
print("columnas           :", list(g.columns))
print("zonas únicas       :", g.zona_mf.nunique(), "| filas duplicadas de zona:",
      int(len(g) - g.zona_mf.nunique()))
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
ZONAS_OK = set(g.zona_mf.str.strip())
print("\nzonas CSV          :", st.zona_mf.nunique(), "| estaciones:", len(st))
print("zonas GPKG == CSV  :", set(st.zona_mf.str.strip()) == ZONAS_OK,
      "| solo GPKG:", sorted(ZONAS_OK - set(st.zona_mf.str.strip())))

# ---------------------------------------------------------------- 2
sep("2. ÁREA TOTAL Y POR ZONA")
rows = []
for i, r in g.iterrows():
    rows.append({"zona_mf": r.zona_mf,
                 "albers_km2": dens_area_km2(r.geometry),
                 "geodesica_km2": geod_area_km2(r.geometry),
                 "epsg6933_km2": gpd.GeoSeries([r.geometry], crs=4326).to_crs(6933).iloc[0].area / 1e6})
A = pd.DataFrame(rows).sort_values("albers_km2", ascending=False)
A["dif_geod_%"] = (A.albers_km2 - A.geodesica_km2) / A.geodesica_km2 * 100
print(A.to_string(index=False, float_format=lambda v: f"{v:,.4f}"))
print(f"\nTOTAL Albers (densificado) : {A.albers_km2.sum():,.4f} km²")
print(f"TOTAL geodésico (elipsoide): {A.geodesica_km2.sum():,.4f} km²")
print(f"TOTAL EPSG:6933            : {A.epsg6933_km2.sum():,.4f} km²")
print(f"desvío Albers vs geodésica : {(A.albers_km2.sum()-A.geodesica_km2.sum())/A.geodesica_km2.sum()*100:+.4f}%")
print(f"desvío 6933 vs geodésica   : {(A.epsg6933_km2.sum()-A.geodesica_km2.sum())/A.geodesica_km2.sum()*100:+.4f}% "
      f"(6933 es área equivalente sobre esfera authálica)")

# ---------------------------------------------------------------- 3
sep("3. PUYUHUPI")
pi = g.index[g.zona_mf == "Puyuhuapi"][0]
puy = g.geometry.iloc[pi]
parts = list(puy.geoms) if puy.geom_type == "MultiPolygon" else [puy]
print(f"partes: {len(parts)}")
for k, p in enumerate(sorted(parts, key=lambda x: -x.area)):
    print(f"  parte {k}: area {dens_area_km2(p):,.4f} km² | geod {geod_area_km2(p):,.4f} km² | "
          f"huecos {len(p.interiors)} | bbox {[round(v,6) for v in p.bounds]}")
print(f"\nárea total Puyuhuapi: {A.loc[A.zona_mf=='Puyuhuapi','albers_km2'].iloc[0]:,.4f} km² (Albers) / "
      f"{A.loc[A.zona_mf=='Puyuhuapi','geodesica_km2'].iloc[0]:,.4f} km² (geodésica)")
print(f"bbox total          : {[round(v,6) for v in puy.bounds]}")
print(f"fragmento atlántico de 11.009,99 km² presente? "
      f"{'SÍ' if any(abs(dens_area_km2(p)-11009.99) < 1.0 for p in parts) else 'NO'}")
print(f"¿alguna parte con lon_max > -70? "
      f"{'SÍ' if any(p.bounds[2] > -70 for p in parts) else 'NO'}")

sp = st[st.zona_mf.str.strip() == "Puyuhuapi"]
dentro = [shapely.contains(puy, q) or shapely.covers(puy, q) for q in sp.geometry]
dd = [dist_geod_punto_geom(q, puy) for q in sp.geometry]
print(f"\nestaciones Puyuhuapi: {len(sp)} | DENTRO: {int(sum(dentro))} | fuera: {int(len(sp)-sum(dentro))}")
print(f"distancia geodésica estación -> polígono: min {min(dd)/1e3:,.3f} km | "
      f"MAX {max(dd)/1e3:,.3f} km | media {np.mean(dd)/1e3:,.3f} km")
if any(x > 0 for x in dd):
    print("  estaciones fuera (estación, km):",
          [(sp.estacion_id.iloc[i], round(dd[i]/1e3, 3)) for i, x in enumerate(dd) if x > 0])

# ---------------------------------------------------------------- 4
sep("4. PARTES SIN ESTACIÓN DE SU ZONA / PARTES MENORES A 1 km²")
PR = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    pts = st[st.zona_mf.str.strip() == key]
    ps = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
    for k, p in enumerate(sorted(ps, key=lambda x: -x.area)):
        n_in = sum(1 for q in pts.geometry if shapely.covers(p, q))
        a = dens_area_km2(p)
        # ¿es la parte más cercana para alguna estación que quedó en tierra?
        just = ""
        if n_in == 0:
            mas_cercana = sum(1 for q in pts.geometry
                              if min(ps, key=lambda x: dist_geod_punto_geom(q, x)).equals(p))
            just = f"respaldada por 'parte más cercana' de {mas_cercana} estación(es) en tierra"
        PR.append({"zona_mf": key, "parte": k, "area_km2": a, "n_est_dentro": n_in,
                   "n_huecos": len(p.interiors),
                   "lon_min": p.bounds[0], "lat_min": p.bounds[1],
                   "lon_max": p.bounds[2], "lat_max": p.bounds[3],
                   "justificacion": just})
P = pd.DataFrame(PR)
print(f"total partes: {len(P)} | zonas con >1 parte: {int((P.groupby('zona_mf').size()>1).sum())} "
      f"| huecos totales: {int(P.n_huecos.sum())}")
sin = P[P.n_est_dentro == 0]
print(f"\nPARTES SIN ESTACIÓN DE SU ZONA: {len(sin)}   {'OK' if len(sin)==0 else '<-- REVISAR'}")
if len(sin):
    print(sin.to_string(index=False, float_format=lambda v: f"{v:,.6f}"))
print("\npartes por zona:")
print(P.groupby("zona_mf").agg(n_partes=("area_km2", "size"),
                               area_km2=("area_km2", "sum"),
                               huecos=("n_huecos", "sum")).to_string(
      float_format=lambda v: f"{v:,.4f}"))
small = P[P.area_km2 < 1.0].sort_values("area_km2")
print(f"\nPARTES MENORES A 1 km²: {len(small)} (suma {small.area_km2.sum():,.6f} km²)")
if len(small):
    print(small[["zona_mf", "parte", "area_km2", "n_est_dentro",
                 "lon_min", "lat_min", "lon_max", "lat_max"]].to_string(
          index=False, float_format=lambda v: f"{v:,.6f}"))
print(f"partes menores a 0,001 km²: {int((P.area_km2 < TOL_KM2).sum())}")

# ---------------------------------------------------------------- 5
sep("5. DISTANCIA GEODÉSICA PARTE -> ESTACIÓN MÁS CERCANA DE SU ZONA (límite 100 km)")
print("Criterio (a) del generador: para cada parte, distancia de la estación más cercana a la parte.")
print("Criterio (b) ESTRICTO: el punto de la parte más alejado de toda estación de su zona.\n")
rows = []
for i, r in g.iterrows():
    key = r.zona_mf.strip()
    pts = st[st.zona_mf.str.strip() == key]
    ps = list(r.geometry.geoms) if r.geometry.geom_type == "MultiPolygon" else [r.geometry]
    # KD-tree para asignar vecino más cercano; distancia final geodésica
    pm = pts.to_crs(UTM)
    S_utm = np.column_stack([pm.geometry.x.values, pm.geometry.y.values])
    tree = cKDTree(S_utm)
    S_ll = np.column_stack([pts.lon.values, pts.lat.values])
    a_max = 0.0; b_max = 0.0; argb = None
    for k, p in enumerate(ps):
        a = min(dist_geod_punto_geom(q, p) for q in pts.geometry) / 1e3
        a_max = max(a_max, a)
        C = shapely.get_coordinates(shapely.segmentize(p, 0.0005))
        minx, miny, maxx, maxy = p.bounds
        gx, gy = np.meshgrid(np.arange(minx, maxx, 0.02), np.arange(miny, maxy, 0.02))
        cand = np.column_stack([gx.ravel(), gy.ravel()])
        C = np.vstack([C, cand[shapely.contains_xy(p, cand[:, 0], cand[:, 1])]])
        Cm = gpd.GeoSeries(gpd.points_from_xy(C[:, 0], C[:, 1]), crs=4326).to_crs(UTM)
        Cu = np.column_stack([Cm.geometry.x.values, Cm.geometry.y.values])
        _, idx = tree.query(Cu)
        _, _, dist = GEOD.inv(C[:, 0], C[:, 1], S_ll[idx][:, 0], S_ll[idx][:, 1])
        j = int(np.argmax(dist))
        if dist[j] / 1e3 > b_max:
            b_max = dist[j] / 1e3; argb = (key, k, round(C[j, 0], 4), round(C[j, 1], 4))
    rows.append({"zona_mf": key, "n_est": len(pts), "n_partes": len(ps),
                 "criterio_a_km": a_max, "criterio_b_km": b_max,
                 "exceso_b_km": max(0.0, b_max - 100),
                 "parte_argmax": argb[1] if argb else None,
                 "lon_argmax": argb[2] if argb else None,
                 "lat_argmax": argb[3] if argb else None})
D = pd.DataFrame(rows).sort_values("criterio_b_km", ascending=False)
print(D.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
print(f"\nMÁXIMO criterio (a): {D.criterio_a_km.max():,.3f} km  "
      f"({D.loc[D.criterio_a_km.idxmax(),'zona_mf']})")
print(f"MÁXIMO criterio (b): {D.criterio_b_km.max():,.3f} km  "
      f"({D.loc[D.criterio_b_km.idxmax(),'zona_mf']})")
print(f"zonas que exceden 100 km -> criterio (a): {D.loc[D.criterio_a_km>100,'zona_mf'].tolist() or 'ninguna'}")
print(f"zonas que exceden 100 km -> criterio (b): {D.loc[D.criterio_b_km>100,'zona_mf'].tolist() or 'ninguna'}")
print("\nzonas con margen < 5 km bajo el límite (criterio b):")
print(D[(D.criterio_b_km > 95) & (D.criterio_b_km <= 100)][["zona_mf", "criterio_b_km"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.3f}"))

# ---------------------------------------------------------------- 6
sep("6. TIERRA RESIDUAL: CON Y SIN set_precision(1e-9)")
c = gpd.read_file(COUNTRIES, engine="pyogrio")
bb = shapely.box(*g.total_bounds).buffer(0.5)
sel = c[c.geometry.intersects(bb)].copy()
print("países/entidades en el bbox+0,5°:", sel.ADMIN.tolist())
land = shapely.make_valid(unary_union([shapely.make_valid(x) for x in sel.geometry]))
land_g = shapely.set_precision(land, GRID)
print("unión tierra válida:", land.is_valid, "| vacía:", land.is_empty)
rows = []
for i, r in g.iterrows():
    ii = shapely.intersection(r.geometry, land)
    ig = shapely.intersection(shapely.set_precision(r.geometry, GRID), land_g)
    rows.append({"zona_mf": r.zona_mf,
                 "sin_rejilla_km2": dens_area_km2(ii) if not ii.is_empty else 0.0,
                 "con_rejilla_km2": dens_area_km2(ig) if not ig.is_empty else 0.0,
                 "n_piezas": (len(ii.geoms) if hasattr(ii, "geoms") else (0 if ii.is_empty else 1))})
T = pd.DataFrame(rows)
raw_sin, raw_con = T.sin_rejilla_km2.sum(), T.con_rejilla_km2.sum()
for col in ["sin_rejilla_km2", "con_rejilla_km2"]:
    T[col] = T[col].mask(T[col].abs() < TOL_KM2, 0.0)
print(T.to_string(index=False, float_format=lambda v: f"{v:,.9f}"))
print(f"\nTOTAL CRUDO sin rejilla: {raw_sin:,.9f} km²  ({raw_sin*1e6:,.1f} m²)")
print(f"TOTAL CRUDO con rejilla: {raw_con:,.9f} km²  ({raw_con*1e6:,.1f} m²)")
print(f"zonas con tierra >= 0,001 km²: sin rejilla "
      f"{T.loc[T.sin_rejilla_km2>0,'zona_mf'].tolist() or 'ninguna'} | con rejilla "
      f"{T.loc[T.con_rejilla_km2>0,'zona_mf'].tolist() or 'ninguna'}")
print("\npor país (intersección en 4326):")
for adm in sel.ADMIN.unique():
    cp = shapely.make_valid(unary_union([shapely.make_valid(x)
                                         for x in sel.loc[sel.ADMIN == adm, "geometry"]]))
    ts = tg = 0.0
    for i, r in g.iterrows():
        ii = shapely.intersection(r.geometry, cp)
        if not ii.is_empty:
            ts += dens_area_km2(ii)
        ig = shapely.intersection(shapely.set_precision(r.geometry, GRID),
                                  shapely.set_precision(cp, GRID))
        if not ig.is_empty:
            tg += dens_area_km2(ig)
    print(f"  {adm:<34} sin {ts:,.9f} km² | con {tg:,.9f} km²")
print("\nCONTROL: área de las zonas fuera de la unión de países (debe ser ~total):")
print(f"  {A.albers_km2.sum() - raw_sin:,.4f} km² dentro de países")

# ---------------------------------------------------------------- 7
sep("7. SOLAPAMIENTO ENTRE ZONAS")
GDf = g.copy()
GDf["geometry"] = [shapely.segmentize(x, 0.005) for x in g.geometry]
ga = GDf.to_crs(ALB)
suma = ga.area.sum() / 1e6
u = unary_union(list(ga.geometry))
print(f"suma de áreas (densificado): {suma:,.6f} km²")
print(f"área de la unión           : {u.area/1e6:,.6f} km²")
print(f"solapamiento               : {suma - u.area/1e6:,.6f} km² "
      f"({(suma-u.area/1e6)*1e6:,.1f} m²)")
pairs = []
for i in range(len(ga)):
    for j in range(i + 1, len(ga)):
        a = shapely.intersection(ga.geometry.iloc[i], ga.geometry.iloc[j]).area / 1e6
        if a > TOL_KM2:
            pairs.append((g.zona_mf.iloc[i], g.zona_mf.iloc[j], a))
print(f"pares con solape > 0,001 km²: {len(pairs)}")
for p in sorted(pairs, key=lambda t: -t[2]):
    print(f"  {p[0]} ∩ {p[1]} = {p[2]:,.6f} km²")
# comprobación en el CRS fuente
ints = [shapely.intersection(g.geometry.iloc[i], g.geometry.iloc[j])
        for i in range(len(g)) for j in range(i + 1, len(g))]
ints = [x for x in ints if not x.is_empty]
print(f"intersecciones no vacías en EPSG:4326: {len(ints)}; tipos: "
      f"{pd.Series([x.geom_type for x in ints]).value_counts().to_dict()}")
print(f"  área máxima de esas intersecciones (4326->Albers densificado): "
      f"{max([dens_area_km2(x) for x in ints]) if ints else 0:,.9f} km²")

# ---------------------------------------------------------------- 8
sep("8. EXPORTACIÓN Y HUELLA FINAL")
A.to_csv(f"{OUT}/areas_v3.csv", index=False)
P.to_csv(f"{OUT}/partes_v3.csv", index=False)
D.to_csv(f"{OUT}/distancias_v3.csv", index=False)
T.to_csv(f"{OUT}/tierra_v3.csv", index=False)
print("csv en", OUT)
MD5_FIN = md5(GPKG)
print("md5 INICIAL:", MD5_INI)
print("md5 FINAL  :", MD5_FIN)
print("¿CAMBIÓ?   :", "NO (intacto)" if MD5_FIN == MD5_INI else "SÍ -- ALERTA")
