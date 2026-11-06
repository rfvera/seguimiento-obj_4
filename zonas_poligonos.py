"""
zonas_poligonos.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera una capa GPKG con polígonos de las zonas de macrofauna usando
tesselación de Voronoi por estación y disolución por zona, recortados
por un área marina que excluye TODA la tierra.

Metodología:
  1. Leer estaciones con zona_mf asignada.
  2. Construir un área marina = bounding box alrededor de todas las
     estaciones MENOS la unión de todos los polígonos de países que
     intersectan ese bbox (Chile, Argentina y cualquier otro). No se
     resta solo Chile: ese era el error que dejaba tierra argentina
     dentro de los polígonos.
  3. Crear polígonos de Voronoi (tesselación) para todas las estaciones,
     recortados al área marina.
  4. Asignar cada región de Voronoi a la zona de su punto generador
     contenido (`contains`/`covers`).
  5. Disolver (unir) todos los polígonos de Voronoi de la misma zona.
  6. Recortar cada zona a la unión de buffers de 100 km alrededor de sus
     estaciones, para evitar extrapolaciones oceánicas sin respaldo
     (fragmento atlántico de Puyuhuapi).
  7. Verificar: geometrías válidas, intersección con tierra ≈ 0,
     solapamiento entre zonas ≈ 0 y distancia máxima a estaciones.

Entradas (solo lectura):
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv
  - salidas/figuras/ne_10m_admin_0_countries.shp (países, Natural Earth 10m)

Salida:
  - salidas/figuras/zonas_macrofauna.gpkg — capa con polígonos de zona (EPSG:4326)
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, MultiPoint, box
from shapely.ops import unary_union, nearest_points
from shapely import make_valid
from pyproj import Geod
from pathlib import Path

GEOD = Geod(ellps="WGS84")

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ESTACIONES = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
GEBCO_CSV = BASE / "gebco_profundidades_marea_roja.csv"
PAISES = BASE / "salidas" / "figuras" / "ne_10m_admin_0_countries.shp"
GSHHG = Path("/tmp/opencode/gshhg_chile/gshhg_chile_high.shp")
SALIDA = BASE / "salidas" / "figuras" / "zonas_macrofauna.gpkg"


def _solo_poligonos(geom):
    """Extrae Polygon/MultiPolygon de una geometría (posible GeometryCollection)."""
    if geom is None or geom.is_empty:
        return None
    if isinstance(geom, (Polygon, MultiPolygon)):
        return geom
    partes = []
    for sub in getattr(geom, "geoms", []):
        p = _solo_poligonos(sub)
        if p is not None and not p.is_empty:
            partes.append(p)
    if not partes:
        return None
    return unary_union(partes)


def crear_area_marina(gdf: gpd.GeoDataFrame, paises_gdf: gpd.GeoDataFrame,
                      margen_grados: float = 0.5):
    """
    Crea un polígono de "área marina" = bounding box grande alrededor de
    todas las estaciones MINUS la unión de todos los países que intersectan
    ese bbox. Restar solo Chile dejaba tierra de Argentina y de otros
    territorios dentro del área marina.
    """
    coords = np.array([(p.x, p.y) for p in gdf.geometry if not p.is_empty])
    if len(coords) == 0:
        raise ValueError("No hay estaciones con coordenadas válidas")

    xmin, ymin = coords.min(axis=0)
    xmax, ymax = coords.max(axis=0)
    bbox = box(
        xmin - margen_grados, ymin - margen_grados,
        xmax + margen_grados, ymax + margen_grados,
    )

    paises_bbox = paises_gdf[paises_gdf.intersects(bbox)].copy()
    if len(paises_bbox) == 0:
        raise ValueError("Ningún país intersecta el bbox de estaciones")

    tierra_ne = unary_union([
        make_valid(g) for g in paises_bbox.geometry
        if g is not None and not g.is_empty
    ])

    tierra = tierra_ne
    if GSHHG.exists():
        gshhg_gdf = gpd.read_file(GSHHG)
        gshhg_bbox = gshhg_gdf[gshhg_gdf.intersects(bbox)].copy()
        if len(gshhg_bbox) > 0:
            tierra_gshhg = unary_union([
                make_valid(g) for g in gshhg_bbox.geometry
                if g is not None and not g.is_empty
            ])
            tierra_comb = make_valid(tierra_ne.intersection(tierra_gshhg))
            if not tierra_comb.is_empty:
                tierra = tierra_comb

    area_marina = _solo_poligonos(make_valid(bbox.difference(tierra)))
    if area_marina is None or area_marina.is_empty:
        raise ValueError("El área marina quedó vacía tras restar la tierra")

    return area_marina, tierra, paises_bbox


def crear_voronoi_por_zona(gdf: gpd.GeoDataFrame, area_marina,
                           tierra) -> gpd.GeoDataFrame:
    """
    Crea polígonos de Voronoi por estación y los recorta al área marina
    (excluyendo toda la tierra). Usa shapely.voronoi_polygons porque no
    exige que todas las estaciones estén dentro del área: las regiones se
    generan sobre el bbox y luego se recortan. Esto evita el fallo de
    geovoronoi con estaciones en fiordos que Natural Earth clasifica como
    tierra.
    """
    puntos = [p for p in gdf.geometry if not p.is_empty]
    zonas = [z for p, z in zip(gdf.geometry, gdf["zona_mf"]) if not p.is_empty]
    if len(puntos) == 0:
        raise ValueError("No hay estaciones con geometría válida")

    # Regiones de Voronoi sobre el bbox del área marina.
    regiones = shapely.voronoi_polygons(
        MultiPoint(puntos), extend_to=area_marina.envelope
    )

    filas = []
    for region in regiones.geoms:
        if region.is_empty:
            continue

        # Asignar la región a la zona de su punto generador contenido.
        idx = [i for i, p in enumerate(puntos) if region.contains(p)]
        if not idx:
            idx = [i for i, p in enumerate(puntos) if region.covers(p)]
        if idx:
            if len(idx) == 1:
                zona_asignada = zonas[idx[0]]
            else:
                c = region.centroid
                j = min(idx, key=lambda i: puntos[i].distance(c))
                zona_asignada = zonas[j]
        else:
            # Punto en el borde o fuera: usar el más cercano al centroide.
            c = region.centroid
            j = min(range(len(puntos)), key=lambda i: puntos[i].distance(c))
            zona_asignada = zonas[j]

        # Recortar al mar y restar cualquier resto de tierra.
        geom = _solo_poligonos(make_valid(region.intersection(area_marina)))
        if geom is None or geom.is_empty:
            continue
        geom = _solo_poligonos(make_valid(geom.difference(tierra)))
        if geom is not None and not geom.is_empty and geom.area > 1e-8:
            filas.append({"zona_mf": zona_asignada, "geometry": geom})

    if len(filas) == 0:
        raise ValueError("No se generó ningún polígono de Voronoi válido.")

    gdf_voronoi = gpd.GeoDataFrame(filas, geometry="geometry", crs="EPSG:4326")
    zonas_disueltas = gdf_voronoi.dissolve(by="zona_mf", as_index=False)
    # Recortar contra tierra también después del dissolve: la unión y la
    # validación pueden reintroducir astillas de borde. set_precision(1e-9)
    # elimina los residuos de ~1 m² sin alterar la costa de forma visible.
    zonas_disueltas["geometry"] = zonas_disueltas.geometry.apply(
        lambda g: _solo_poligonos(
            shapely.set_precision(
                make_valid(make_valid(g).difference(tierra)), 1e-9
            )
        )
    )
    zonas_disueltas = zonas_disueltas[
        zonas_disueltas.geometry.notna() & ~zonas_disueltas.geometry.is_empty
    ].reset_index(drop=True)

    return zonas_disueltas


def _buffer_geodesico(punto, radio_m: float, n: int = 72) -> Polygon:
    """Círculo geodésico aproximado de radio `radio_m` alrededor de un punto."""
    lons, lats = [], []
    for az in np.linspace(0, 360, n, endpoint=False):
        lon, lat, _ = GEOD.fwd(punto.x, punto.y, float(az), radio_m)
        lons.append(lon)
        lats.append(lat)
    return Polygon(zip(lons, lats))


def _dist_geod(punto, geom) -> float:
    """Distancia geodésica mínima (m) de un punto a una geometría."""
    q = nearest_points(punto, geom)[1]
    return GEOD.inv(punto.x, punto.y, q.x, q.y)[2]


def _conservar_partes(geom, puntos, area_marina):
    """
    Conserva las partes del polígono que están conectadas por mar a una
    parte ancla (la que contiene una estación, o la más cercana si todas
    caen en tierra). Una parte al otro lado de una barrera terrestre está
    en otra componente conexa de `area_marina` y se descarta; una parte
    sin estación pero en la misma componente (agua adyacente) se conserva.
    """
    if geom is None or geom.is_empty:
        return None

    partes = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]

    # Partes ancla: las que contienen al menos una estación.
    anclas = [p for p in partes if any(p.covers(pt) for pt in puntos)]
    if not anclas:
        # Todas las estaciones caen en tierra: usar la parte más cercana.
        mejor = min(partes, key=lambda p: min(_dist_geod(pt, p) for pt in puntos))
        anclas = [mejor]

    comps = (
        list(area_marina.geoms)
        if area_marina.geom_type == "MultiPolygon"
        else [area_marina]
    )

    seleccionadas = list(anclas)
    for parte in partes:
        if any(parte.equals(a) for a in anclas):
            continue
        comp = None
        rp = parte.representative_point()
        for c in comps:
            if c.contains(rp) or c.intersects(parte):
                comp = c
                break
        if comp is None:
            continue
        # Conservar solo si la componente marina contiene un ancla.
        if any(
            comp.contains(a.representative_point()) or comp.intersects(a)
            for a in anclas
        ):
            seleccionadas.append(parte)

    if not seleccionadas:
        return None
    return unary_union(seleccionadas)


def recortar_por_distancia(zonas_gdf: gpd.GeoDataFrame,
                           estaciones: gpd.GeoDataFrame,
                           tierra,
                           area_marina,
                           buffer_km: float = 100.0) -> gpd.GeoDataFrame:
    """
    Recorta cada polígono de zona a la unión de buffers geodésicos de
    `buffer_km` alrededor de las estaciones de esa zona. El buffer se genera
    con pyproj.Geod, no en EPSG:6933, para que el radio sea real en todas
    las direcciones (en 6933 un "buffer de 100 km" resulta una elipse de
    ~148 km N-S por ~66 km E-O a estas latitudes). Después se conservan solo
    las partes respaldadas por estaciones de la zona.
    """
    filas = []
    for _, row in zonas_gdf.iterrows():
        zona = row["zona_mf"]
        pts = list(estaciones.loc[estaciones["zona_mf"] == zona, "geometry"])
        if len(pts) == 0:
            continue

        buf = unary_union([
            _buffer_geodesico(p, buffer_km * 1000.0) for p in pts
        ])

        geom = _solo_poligonos(
            make_valid(make_valid(row.geometry).intersection(buf))
        )
        if geom is None or geom.is_empty:
            continue
        geom = _solo_poligonos(make_valid(geom.difference(tierra)))
        if geom is None or geom.is_empty:
            continue

        # Descartar partes al otro lado de una barrera terrestre sin respaldo.
        geom = _conservar_partes(geom, pts, area_marina)
        if geom is None or geom.is_empty:
            continue

        geom = _solo_poligonos(shapely.set_precision(geom, 1e-9))
        if geom is not None and not geom.is_empty and geom.area > 1e-8:
            filas.append({"zona_mf": zona, "geometry": geom})

    if not filas:
        raise ValueError("El recorte por distancia dejó la capa vacía")

    return gpd.GeoDataFrame(
        filas, geometry="geometry", crs="EPSG:4326"
    ).reset_index(drop=True)


def _area_km2(geom) -> float:
    """Área en km² reproyectando a EPSG:6933 (equal-area)."""
    serie = gpd.GeoSeries([geom], crs="EPSG:4326").to_crs(6933)
    return float(serie.iloc[0].area / 1e6)


def main():
    print("Leyendo estaciones...")
    est = pd.read_csv(ESTACIONES)
    est["lat"] = pd.to_numeric(est["lat"], errors="coerce")
    est["lon"] = pd.to_numeric(est["lon"], errors="coerce")
    est = est.dropna(subset=["lat", "lon"])

    gebco_depths = {}
    if GEBCO_CSV.exists():
        gb = pd.read_csv(GEBCO_CSV, dtype={"CODIGO": str})
        for _, row in gb.iterrows():
            gebco_depths[str(row["CODIGO"])] = row["profundidad_fondo_m"]

    def es_agua(sid):
        if str(sid) in gebco_depths:
            return bool(gebco_depths[str(sid)] < 0)
        return True

    est["en_agua"] = est["estacion_id"].apply(es_agua)
    print(f"Estaciones en agua: {est['en_agua'].sum()} de {len(est)}")

    gdf = gpd.GeoDataFrame(
        est,
        geometry=gpd.points_from_xy(est["lon"], est["lat"]),
        crs="EPSG:4326",
    )
    print(f"Estaciones: {len(gdf)}")
    print(f"Zonas: {gdf['zona_mf'].nunique()}")

    print("Leyendo países (Natural Earth 10m)...")
    paises = gpd.read_file(str(PAISES))
    if paises.crs is None:
        paises = paises.set_crs("EPSG:4326")
    elif paises.crs.to_epsg() != 4326:
        paises = paises.to_crs("EPSG:4326")

    print("Creando área marina (bbox - todos los países que intersectan)...")
    area_marina, tierra, paises_bbox = crear_area_marina(gdf, paises, margen_grados=0.5)
    print(f"Países que intersectan el bbox: {len(paises_bbox)} -> "
          f"{sorted(paises_bbox['ADM0_A3'].tolist())}")
    print(f"Área marina: {area_marina.area:.4f} grados² | tipo: {area_marina.geom_type}")

    print("Generando polígonos de Voronoi por zona...")
    zonas_gdf = crear_voronoi_por_zona(gdf, area_marina, tierra)
    print(f"Polígonos de zona generados: {len(zonas_gdf)}")

    print("Recortando cada zona a 100 km alrededor de sus estaciones...")
    zonas_gdf = recortar_por_distancia(
        zonas_gdf, gdf, tierra, area_marina, buffer_km=100.0
    )
    print(f"Polígonos tras recorte de distancia: {len(zonas_gdf)}")

    # --- Verificación de solapamientos ---
    print("Verificando solapamientos...")
    areas = zonas_gdf.geometry.area
    union = unary_union(zonas_gdf.geometry)
    solapamiento = float(areas.sum() - union.area)
    print(f"Área suma de polígonos: {areas.sum():.6f} grados²")
    print(f"Área de unión: {union.area:.6f} grados²")
    print(f"Área de solapamiento: {solapamiento:.6f} grados²")
    if abs(solapamiento) < 1e-6:
        print("OK: No hay solapamientos significativos entre zonas.")
    else:
        print("ADVERTENCIA: Hay solapamientos entre zonas.")

    # --- Verificación de tierra ---
    print("\nVerificando intersección con tierra (km²)...")
    tierra_verif = shapely.set_precision(tierra, 1e-9)
    total_tierra = 0.0
    for _, row in zonas_gdf.iterrows():
        g = shapely.set_precision(make_valid(row.geometry), 1e-9)
        inter = g.intersection(tierra_verif)
        if not inter.is_empty:
            total_tierra += _area_km2(inter)
    print(f"Tierra total dentro de los polígonos: {total_tierra:.8f} km²")
    if total_tierra < 0.01:
        print("OK: Los polígonos no contienen tierra firme.")
    else:
        print("ADVERTENCIA: Los polígonos todavía contienen tierra.")

    # --- Verificación de distancia a las estaciones (geodésica) ---
    print("\nVerificando distancia de estaciones y partes a su zona...")
    max_est = 0.0
    max_parte = 0.0
    for _, row in zonas_gdf.iterrows():
        pts = list(gdf.loc[gdf["zona_mf"] == row["zona_mf"], "geometry"])
        if len(pts) == 0:
            continue
        geom = row.geometry
        max_est = max(max_est, max(_dist_geod(p, geom) for p in pts))
        partes = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        for parte in partes:
            max_parte = max(max_parte, min(_dist_geod(p, parte) for p in pts))
    print(f"Distancia máxima estación -> su polígono: {max_est/1000:.2f} km")
    print(f"Distancia máxima parte -> estación más cercana de su zona: "
          f"{max_parte/1000:.2f} km")
    if max_parte / 1000.0 <= 100.01:
        print("OK: Ninguna parte excede el buffer geodésico de 100 km.")
    else:
        print("ADVERTENCIA: Hay partes a más de 100 km de una estación de su zona.")

    # --- Verificación topológica: partes sin estación conectadas por mar ---
    print("\nVerificando partes sin estación y su conectividad marina...")
    comps = (
        list(area_marina.geoms)
        if area_marina.geom_type == "MultiPolygon"
        else [area_marina]
    )
    sin_total = 0
    sin_mal = 0
    for _, row in zonas_gdf.iterrows():
        pts = list(gdf.loc[gdf["zona_mf"] == row["zona_mf"], "geometry"])
        partes = (
            list(row.geometry.geoms)
            if row.geometry.geom_type == "MultiPolygon"
            else [row.geometry]
        )
        anclas = [p for p in partes if any(p.covers(pt) for pt in pts)]
        if not anclas:
            anclas = [
                min(partes, key=lambda p: min(_dist_geod(pt, p) for pt in pts))
            ]
        for parte in partes:
            if any(parte.equals(a) for a in anclas):
                continue
            sin_total += 1
            rp = parte.representative_point()
            comp = next(
                (c for c in comps if c.contains(rp) or c.intersects(parte)),
                None,
            )
            if comp is None or not any(
                comp.contains(a.representative_point()) or comp.intersects(a)
                for a in anclas
            ):
                sin_mal += 1
    print(f"Partes sin estación conservadas: {sin_total}")
    print(f"Partes sin estación en componentes sin ancla: {sin_mal}")
    if sin_mal == 0:
        print("OK: Toda parte sin estación está conectada por mar a un ancla.")
    else:
        print("ADVERTENCIA: Hay partes sin estación separadas por tierra.")

    # --- Post-procesamiento: estaciones en fiordos ---
    print("\nPost-procesamiento: incluyendo estaciones en fiordos...")
    est_fuera = []
    for _, row in gdf.iterrows():
        zona_row = zonas_gdf[zonas_gdf["zona_mf"] == row["zona_mf"]]
        if len(zona_row) == 0:
            est_fuera.append(row)
            continue
        if not (zona_row.geometry.iloc[0].contains(row.geometry) or
                zona_row.geometry.iloc[0].covers(row.geometry)):
            est_fuera.append(row)
    print(f"  Estaciones fuera de su zona: {len(est_fuera)}")

    for row in est_fuera:
        zona = row["zona_mf"]
        pt = row.geometry
        buf = pt.buffer(0.001)  # ~500 m en grados
        idx = zonas_gdf[zonas_gdf["zona_mf"] == zona].index[0]
        geom = zonas_gdf.loc[idx, "geometry"]
        zonas_gdf.loc[idx, "geometry"] = geom.union(buf)

    # --- Guardar ---
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    zonas_gdf.to_file(SALIDA, driver="GPKG")
    print(f"\nGuardado: {SALIDA}")
    print(f"Columnas: {zonas_gdf.columns.tolist()}")
    print(f"Zonas ({len(zonas_gdf)}): {sorted(zonas_gdf['zona_mf'].tolist())}")


if __name__ == "__main__":
    main()
