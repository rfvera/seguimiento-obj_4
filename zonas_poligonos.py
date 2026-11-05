"""
zonas_poligonos.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera una capa GPKG con polígonos de las zonas de macrofauna usando
tesselación de Voronoi por estación y disolución por zona.

Metodología:
  1. Leer estaciones con zona_mf asignada
  2. Crear polígonos de Voronoi (tesselación) para todas las estaciones
  3. Asignar cada polígono de Voronoi a la zona de su estación
  4. Disolver (unir) todos los polígonos de Voronoi de la misma zona
  5. Resultado: polígonos de zona que NO se solapan entre sí

Entradas (solo lectura):
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv

Salida:
  - salidas/figuras/zonas_macrofauna.gpkg — capa con polígonos de zona (EPSG:4326)
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, MultiPoint, Polygon
from shapely.ops import unary_union
from scipy.spatial import Voronoi
from pathlib import Path

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ESTACIONES = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
SALIDA = BASE / "salidas" / "figuras" / "zonas_macrofauna.gpkg"


def crear_voronoi_por_zona(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Crea polígonos de Voronoi por estación y los disuelve por zona.
    Los polígonos resultantes NO se solapan entre sí.
    """
    # Obtener puntos y sus zonas
    puntos = list(gdf.geometry)
    zonas = gdf["zona_mf"].tolist()

    # Filtrar puntos vacíos
    puntos_validos = [(p.x, p.y, z) for p, z in zip(puntos, zonas) if not p.is_empty]

    # Crear un MultiPoint de todas las estaciones
    coords = np.array([(px, py) for px, py, _ in puntos_validos])
    zonas_lista = [z for _, _, z in puntos_validos]

    # Bounding box con margen
    xmin, ymin = coords.min(axis=0)
    xmax, ymax = coords.max(axis=0)
    margen = 0.5  # grados
    bbox = Polygon.from_bounds(
        xmin - margen, ymin - margen, xmax + margen, ymax + margen
    )

    # Generar Voronoi con scipy
    vor = Voronoi(coords)

    # Crear polígonos de Voronoi recortados al bbox
    filas = []
    for region_idx in vor.regions:
        if -1 in region_idx or len(region_idx) == 0:
            continue  # regiones infinitas (abiertas)

        poligono = Polygon([vor.vertices[i] for i in region_idx])
        poligono = poligono.intersection(bbox)

        if poligono.is_empty or poligono.area < 1e-10:
            continue

        # Encontrar el punto generador más cercano para asignar la zona
        cent = poligono.centroid
        dist_min = float("inf")
        zona_asignada = None
        for px, py, z in puntos_validos:
            d = cent.distance(Point(px, py))
            if d < dist_min:
                dist_min = d
                zona_asignada = z

        filas.append({"zona_mf": zona_asignada, "geometry": poligono})

    gdf_voronoi = gpd.GeoDataFrame(filas, crs="EPSG:4326")

    # Disolver (unir) por zona_mf -> polígonos que NO se solapan
    zonas_disueltas = gdf_voronoi.dissolve(by="zona_mf", as_index=False)

    return zonas_disueltas


def main():
    print("Leyendo estaciones...")
    est = pd.read_csv(ESTACIONES)
    est["lat"] = pd.to_numeric(est["lat"], errors="coerce")
    est["lon"] = pd.to_numeric(est["lon"], errors="coerce")
    est = est.dropna(subset=["lat", "lon"])

    gdf = gpd.GeoDataFrame(
        est,
        geometry=gpd.points_from_xy(est["lon"], est["lat"]),
        crs="EPSG:4326",
    )
    print(f"Estaciones: {len(gdf)}")
    print(f"Zonas: {gdf['zona_mf'].nunique()}")

    print("Generando polígonos de Voronoi por zona...")
    zonas_gdf = crear_voronoi_por_zona(gdf)
    print(f"Polígonos de zona generados: {len(zonas_gdf)}")

    # Verificar que no haya solapamientos
    print("Verificando solapamientos...")
    areas = zonas_gdf.geometry.area
    union = unary_union(zonas_gdf.geometry)
    area_union = union.area
    area_suma = areas.sum()
    solapamiento = area_suma - area_union
    print(f"Área suma de polígonos: {area_suma:.6f}")
    print(f"Área de unión: {area_union:.6f}")
    print(f"Área de solapamiento: {solapamiento:.6f}")
    if abs(solapamiento) < 1e-6:
        print("OK: No hay solapamientos significativos entre zonas.")
    else:
        print("ADVERTENCIA: Hay solapamientos entre zonas.")

    # Guardar
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    zonas_gdf.to_file(SALIDA, driver="GPKG")
    print(f"\nGuardado: {SALIDA}")
    print(f"Columnas: {zonas_gdf.columns.tolist()}")
    print(f"Zonas: {sorted(zonas_gdf['zona_mf'].tolist())}")


if __name__ == "__main__":
    main()
