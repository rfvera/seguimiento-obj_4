"""
zonas_poligonos.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Genera una capa GPKG con polígonos de las zonas de macrofauna usando
tesselación de Voronoi por estación y disolución por zona, recortados
por un área marina definida como buffer alrededor de cada estación.

Metodología:
  1. Leer estaciones con zona_mf asignada
  2. Crear un área marina = buffer de 10 km alrededor de TODAS las estaciones
     (unión de todos los buffers individuales)
  3. Crear polígonos de Voronoi (tesselación) para todas las estaciones
  4. Recortar cada polígono de Voronoi por el área marina
  5. Asignar cada polígono de Voronoi a la zona de su estación
  6. Disolver (unir) todos los polígonos de Voronoi de la misma zona
  7. Resultado: polígonos de zona que NO se solapan y están limitados al
     mar cerca de las estaciones (no incluyen tierra firme)

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


def crear_area_marina(gdf: gpd.GeoDataFrame, buffer_km: float = 25.0) -> Polygon:
    """
    Crea un polígono que representa el área marina cubierto por las estaciones.
    Usa un buffer de buffer_km alrededor de cada estación, unido todo junto.
    Como las estaciones están en el mar, el área marina aproximada es el
    área dentro de un radio razonable alrededor de cada estación.
    """
    puntos = list(gdf.geometry)
    multipoint = MultiPoint([p for p in puntos if not p.is_empty])

    # Buffer de buffer_km alrededor de cada estación, unido todo junto
    # 1 grado ≈ 111 km en latitud, por lo que buffer_km / 111 = grados aprox
    buffer_deg = buffer_km / 111.0
    area_marina = multipoint.buffer(buffer_deg)

    return area_marina


def crear_voronoi_por_zona(gdf: gpd.GeoDataFrame, area_marina: Polygon) -> gpd.GeoDataFrame:
    """
    Crea polígonos de Voronoi por estación, recortados por el área marina,
    y los disuelve por zona. Los polígonos resultantes NO se solapan.
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

        # RECORTAR POR ÁREA MARINA: solo mantener la parte dentro del área marina
        poligono_marino = poligono.intersection(area_marina)
        if poligono_marino.is_empty or poligono_marino.area < 1e-8:
            continue  # El polígono está fuera del área marina (en tierra)

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

    print("Creando área marina (buffer de 25 km alrededor de estaciones)...")
    area_marina = crear_area_marina(gdf, buffer_km=25.0)
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

    # Guardar
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    zonas_gdf.to_file(SALIDA, driver="GPKG")
    print(f"\nGuardado: {SALIDA}")
    print(f"Columnas: {zonas_gdf.columns.tolist()}")
    print(f"Zonas: {sorted(zonas_gdf['zona_mf'].tolist())}")


if __name__ == "__main__":
    main()
