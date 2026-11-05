"""
zonas_poligonos.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera una capa GPKG con polígonos de las zonas de macrofauna usando
tesselación de Voronoi por estación y disolución por zona, recortados
por un área marina = bounding box grande de las estaciones MINUS el
polígono del país Chile (Natural Earth 10m).

Metodología:
  1. Leer estaciones con zona_mf asignada
  2. Crear un polígono de "área marina" = bounding box grande alrededor de
     todas las estaciones MINUS el polígono del país Chile
  3. Crear polígonos de Voronoi (tesselación) para todas las estaciones
  4. Recortar cada polígono de Voronoi por el área marina
  5. Asignar cada polígono de Voronoi a la zona de su estación
  6. Disolver (unir) todos los polígonos de Voronoi de la misma zona
  7. Resultado: polígonos de zona que NO se solapan y son ADYACENTES entre sí,
     cubriendo todo el área marina de estudio (para extrapolación)

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
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import unary_union
from scipy.spatial import Voronoi
from pathlib import Path

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ESTACIONES = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
PAISES = BASE / "salidas" / "figuras" / "ne_10m_admin_0_countries.shp"
SALIDA = BASE / "salidas" / "figuras" / "zonas_macrofauna.gpkg"


def crear_area_marina(gdf: gpd.GeoDataFrame, paises_gdf: gpd.GeoDataFrame,
                      margen_grados: float = 0.5) -> Polygon:
    """
    Crea un polígono de "área marina" = bounding box grande alrededor de
    todas las estaciones MINUS el polígono del país Chile.

    Esto crea un área continua que cubre toda la región de estudio sin
    incluir tierra firme.
    """
    # Obtener coordenadas de todas las estaciones
    puntos = list(gdf.geometry)
    coords = np.array([(p.x, p.y) for p in puntos if not p.is_empty])

    # Bounding box grande alrededor de todas las estaciones con margen
    xmin, ymin = coords.min(axis=0)
    xmax, ymax = coords.max(axis=0)
    bbox = Polygon.from_bounds(
        xmin - margen_grados, ymin - margen_grados,
        xmax + margen_grados, ymax + margen_grados
    )

    # Obtener el polígono de Chile
    chile = paises_gdf[paises_gdf["ADM0_A3"] == "CHL"]
    if len(chile) == 0:
        chile = paises_gdf[paises_gdf["NAME"].str.contains("Chile", case=False, na=False)]
    if len(chile) == 0:
        raise ValueError("No se encontró Chile en el shapefile de países")

    chile_union = chile.geometry.unary_union

    # Área marina = bounding box MINUS Chile (tierra)
    area_marina = bbox.difference(chile_union)

    return area_marina


def crear_voronoi_por_zona(gdf: gpd.GeoDataFrame, area_marina: Polygon) -> gpd.GeoDataFrame:
    """
    Crea polígonos de Voronoi por estación, recortados por el área marina,
    y los disuelve por zona.

    Como el área marina es un polígono continuo (sin agujeros internos
    excepto la tierra de Chile que ya se restó), los polígonos de Voronoi
    resultantes son ADYACENTES entre sí y cubren todo el área marina.

    Los polígonos resultantes NO se solapan entre sí.
    """
    # Obtener puntos y sus zonas
    puntos = list(gdf.geometry)
    zonas = gdf["zona_mf"].tolist()

    # Filtrar puntos vacíos
    puntos_validos = [(p.x, p.y, z) for p, z in zip(puntos, zonas) if not p.is_empty]

    # Coordenadas para Voronoi
    coords = np.array([(px, py) for px, py, _ in puntos_validos])

    # Generar Voronoi con scipy
    vor = Voronoi(coords)

    # Crear polígonos de Voronoi recortados por el área marina
    filas = []
    for region_idx in vor.regions:
        if -1 in region_idx or len(region_idx) == 0:
            continue  # regiones infinitas (abiertas)

        poligono = Polygon([vor.vertices[i] for i in region_idx])

        # RECORTAR POR ÁREA MARINA
        poligono_marino = poligono.intersection(area_marina)
        if poligono_marino.is_empty or poligono_marino.area < 1e-8:
            continue  # El polígono está completamente fuera del área marina

        # Encontrar el punto generador más cercano para asignar la zona
        cent = poligono_marino.centroid
        dist_min = float("inf")
        zona_asignada = None
        for px, py, z in puntos_validos:
            d = cent.distance(Point(px, py))
            if d < dist_min:
                dist_min = d
                zona_asignada = z

        filas.append({"zona_mf": zona_asignada, "geometry": poligono_marino})

    if len(filas) == 0:
        raise ValueError("No se generó ningún polígono de Voronoi válido después del recorte por área marina.")

    gdf_voronoi = gpd.GeoDataFrame(filas, geometry="geometry", crs="EPSG:4326")

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

    print("Leyendo polígono de Chile (Natural Earth 10m)...")
    paises = gpd.read_file(str(PAISES))
    chile = paises[paises["ADM0_A3"] == "CHL"]
    if len(chile) == 0:
        chile = paises[paises["NAME"].str.contains("Chile", case=False, na=False)]
    print(f"Chile encontrado: {len(chile)} feature(s)")

    print("Creando área marina (bounding box grande - Chile)...")
    area_marina = crear_area_marina(gdf, chile, margen_grados=0.5)
    print(f"Área marina creada: {area_marina.area:.4f} grados cuadrados")

    print("Generando polígonos de Voronoi por zona (recortados por área marina)...")
    zonas_gdf = crear_voronoi_por_zona(gdf, area_marina)
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

    # Verificar que los polígonos son adyacentes (comparten bordes)
    print("Verificando adyacencia...")
    from shapely.geometry import LineString
    tocando = 0
    zonas_list = list(zonas_gdf.geometry)
    for i in range(len(zonas_list)):
        for j in range(i + 1, len(zonas_list)):
            inter = zonas_list[i].intersection(zonas_list[j])
            if inter.geom_type == "LineString" and inter.length > 0.001:
                tocando += 1
    print(f"Pares de zonas adyacentes (comparten borde): {tocando}")

    # Guardar
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    zonas_gdf.to_file(SALIDA, driver="GPKG")
    print(f"\nGuardado: {SALIDA}")
    print(f"Columnas: {zonas_gdf.columns.tolist()}")
    print(f"Zonas: {sorted(zonas_gdf['zona_mf'].tolist())}")


if __name__ == "__main__":
    main()
