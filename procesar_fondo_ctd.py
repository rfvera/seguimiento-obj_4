"""
procesar_fondo_ctd.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Objetivo:
  Extraer el registro de fondo (profundidad maxima registrada) por estacion x fecha
  de dos archivos CTD y unir cada registro con la zona asignada previamente.

Entradas:
  1. Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx  (hoja 'Base de Datos CTD2019-2025_IFOP')
  2. datos CTD - marea roja.xlsx                   (hoja 'Datos CTD')
  3. estaciones_CTD_con_zona_final.csv

Salida:
  fondo_ctd_por_zona.csv

Reglas:
  - Nunca inventar datos. Sin match de zona -> zona NaN, reportado.
  - pandas. Codigo reproducible. Semilla fija no aplica (no hay muestreo aleatorio).
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ARCH_A = BASE / "Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx"
ARCH_B = BASE / "datos CTD - marea roja.xlsx"
ZONAS  = BASE / "estaciones_CTD_con_zona_final.csv"
SALIDA = BASE / "fondo_ctd_por_zona.csv"

# ---------------------------------------------------------------------------
# 1. Lectura archivo A
# ---------------------------------------------------------------------------
def leer_archivo_a(path: Path) -> pd.DataFrame:
    """Lee la hoja de datos del archivo A.
    Filas 0-19 = metadatos, fila 20 (0-indexed) = encabezado, datos desde fila 21.
    """
    raw = pd.read_excel(path, sheet_name="Base de Datos CTD2019-2025_IFOP", header=None)
    if raw.shape[0] <= 21:
        raise ValueError(f"Archivo A no tiene el encabezado esperado en la fila 20: {raw.shape}")
    header = raw.iloc[20].tolist()
    df = raw.iloc[21:].copy()
    df.columns = header

    # Renombrar por posicion para evitar la columna sin nombre (col 7) y el
    # duplicado ESTACION (col 28). Se usa la col 6 como ESTACION.
    nombres = [
        "Año", "NOMB_PROY", "COD_PROY", "FECHA_INICIO", "FECHA_TERMINO", "EQUIPO",
        "ESTACION", "FLAG_BOOL", "LATITUD", "LONGITUD", "PROF_EQ_m",
        "PROF_SECT_m", "TEMPERATURA_C", "OXIG_ml_L", "OXIG_mg_L", "OXIG_pct_sat",
        "OX_umol_kg", "SALINIDAD_psu", "FLUORESCEN_mg_m3", "DENSIDAD_sigma_t",
        "CLOROFILA_mg_m3", "FEOPIGMEN_mg_m3", "NITRATO_uM", "FOSFATO_uM",
        "SILICATO_uM", "pH", "COD_REG", "OBSERV", "ESTACION_DUP", "HORA_DATO",
        "DISCO_SECH_m",
    ]
    if len(nombres) != df.shape[1]:
        raise ValueError(f"Esperaba {len(nombres)} columnas, leí {df.shape[1]}")
    df.columns = nombres

    # Tipos
    df["ESTACION"] = pd.to_numeric(df["ESTACION"], errors="coerce")
    df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"], errors="coerce")
    df["PROF_EQ_m"] = pd.to_numeric(df["PROF_EQ_m"], errors="coerce")
    for c in ["TEMPERATURA_C", "OXIG_ml_L", "OXIG_mg_L", "SALINIDAD_psu"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# 2. Lectura archivo B
# ---------------------------------------------------------------------------
def leer_archivo_b(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Datos CTD", header=0)

    # FECHA: mixto (datetime y string 'DD-MM-YYYY'); 'S/I' = sin informacion -> NaT
    def parse_fecha(x):
        if isinstance(x, str):
            x = x.strip()
            if x == "" or x.upper() == "S/I":
                return pd.NaT
            return pd.to_datetime(x, format="%d-%m-%Y", errors="coerce")
        return pd.to_datetime(x, errors="coerce")

    df["FECHA"] = df["FECHA"].apply(parse_fecha)

    df["CODIGO"] = df["CODIGO"].astype(str).str.strip()
    df["PROFUNDIDAD_m"] = pd.to_numeric(df["PROFUNDIDAD (m)"], errors="coerce")
    for c in ["TEMPERATURA (C°)", "SALINIDAD (PSU)", "OXIGENO (ml/L)"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.rename(columns={
        "TEMPERATURA (C°)": "TEMPERATURA_C",
        "SALINIDAD (PSU)": "SALINIDAD_psu",
        "OXIGENO (ml/L)": "OXIGENO_ml_L",
    })
    return df


# ---------------------------------------------------------------------------
# 3. Registro de fondo por estacion x fecha
# ---------------------------------------------------------------------------
def registro_fondo(df: pd.DataFrame, estacion_col: str, fecha_col: str,
                   prof_col: str, archivo: str,
                   var_map: dict, fondo_col: str | None = None) -> pd.DataFrame:
    """Para cada (estacion, fecha) se queda con la fila de profundidad maxima de
    medicion (prof_col) y reporta la profundidad de fondo (fondo_col).

    - prof_col: columna de profundidad de cada medicion del perfil CTD. Se usa
      para seleccionar la fila mas profunda (idxmax) de la que se toman las
      variables (temperatura, oxigeno, salinidad).
    - fondo_col: columna con la profundidad de fondo (carta/ecosonda) por grupo.
      Si es None (archivo B marea roja), profundidad_fondo_m queda NaN porque
      los perfiles no llegan al fondo y no hay dato de fondo en el archivo.
    var_map: diccionario {columna_origen: columna_salida} para las variables.
    """
    n_total = len(df)
    n_fecha_nula = int(df[fecha_col].isna().sum())
    n_prof_nula = int(df[prof_col].isna().sum())

    # Solo filas con fecha y profundidad de medicion validas entran en la agrupacion
    val = df.dropna(subset=[estacion_col, fecha_col, prof_col]).copy()
    n_val = len(val)

    # idx de la profundidad maxima de medicion por grupo (primer fila en caso
    # de empate; decision documentada y determinista).
    idx = val.groupby([estacion_col, fecha_col])[prof_col].idxmax()
    fondo = val.loc[idx].copy()

    # Profundidad de fondo: valor de fondo_col en la fila seleccionada. Cuando
    # un grupo tiene varios valores de fondo_col (diferentes campañas), se toma
    # el maximo (profundidad de fondo más profunda declarada).
    if fondo_col is not None and fondo_col in val.columns:
        fondo_map = (
            val.groupby([estacion_col, fecha_col])[fondo_col]
            .max()
            .rename("profundidad_fondo_m")
        )
        fondo = fondo.merge(
            fondo_map, on=[estacion_col, fecha_col], how="left"
        )
        fondo_fuente = fondo_col
    else:
        fondo["profundidad_fondo_m"] = pd.NA
        fondo_fuente = None

    # Detectar empates reales en la profundidad maxima de medicion por (estacion, fecha).
    tamanos = val.groupby([estacion_col, fecha_col])[prof_col].transform("max")
    en_max = val[prof_col] == tamanos
    n_grupos_empate = int(val[en_max].groupby([estacion_col, fecha_col]).size().gt(1).sum()) if len(val) else 0
    # Cuantos de esos grupos empatados tienen filas con valores distintos de
    # las variables de interes (por lo que la regla de desempate afecta el dato).
    n_empate_afecta_var = 0
    if n_grupos_empate > 0:
        for (est, fec), sub in val[en_max].groupby([estacion_col, fecha_col]):
            if len(sub) > 1:
                cambia = any(sub[src].nunique(dropna=True) > 1 for src in var_map.keys() if src in val.columns)
                if cambia:
                    n_empate_afecta_var += 1

    out = pd.DataFrame({
        "archivo": archivo,
        "estacion_id": fondo[estacion_col].astype(str),
        "fecha": fondo[fecha_col],
        "profundidad_fondo_m": fondo["profundidad_fondo_m"],
    })
    if fondo_fuente is not None:
        out["profundidad_fondo_fuente"] = fondo_fuente
    else:
        out["profundidad_fondo_fuente"] = "no_disponible"
    for src, dst in var_map.items():
        out[dst] = fondo[src].values

    resumen = {
        "archivo": archivo,
        "n_filas_totales": n_total,
        "n_fecha_nula": n_fecha_nula,
        "n_profundidad_nula": n_prof_nula,
        "n_filas_validas_agrupacion": n_val,
        "n_estacion_fecha": len(fondo),
        "n_grupos_con_empate_prof_max": n_grupos_empate,
        "n_empate_afecta_variables": n_empate_afecta_var,
        "regla_desempate": "primera fila en orden de lectura (idxmax)",
        "fondo_col": fondo_col,
    }
    return out, resumen


# ---------------------------------------------------------------------------
# 4. Union con zonas
# ---------------------------------------------------------------------------
def unir_con_zonas(fondo: pd.DataFrame, zonas: pd.DataFrame) -> pd.DataFrame:
    zonas_u = zonas[["archivo", "estacion_id", "zona", "zona_tipo", "dist_km", "fuente"]].copy()
    zonas_u["estacion_id"] = zonas_u["estacion_id"].astype(str).str.strip()
    fondo["estacion_id"] = fondo["estacion_id"].astype(str).str.strip()

    merged = fondo.merge(zonas_u, on=["archivo", "estacion_id"], how="left")
    n_sin_zona = int(merged["zona"].isna().sum())
    return merged, n_sin_zona


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    zonas = pd.read_csv(ZONAS, dtype={"estacion_id": str})
    print(f"Zonas cargadas: {zonas.shape} | A={int((zonas.archivo=='A').sum())} B={int((zonas.archivo=='B').sum())}")

    # --- Archivo A ---
    dfA = leer_archivo_a(ARCH_A)
    print(f"\nArchivo A leido: {dfA.shape}")
    print(f"  ESTACION: nula={dfA['ESTACION'].isna().sum()}, rango={dfA['ESTACION'].min()}-{dfA['ESTACION'].max()}")
    print(f"  FECHA_INICIO: nula={dfA['FECHA_INICIO'].isna().sum()}, rango={dfA['FECHA_INICIO'].min()} a {dfA['FECHA_INICIO'].max()}")
    print(f"  PROF_EQ_m: nula={dfA['PROF_EQ_m'].isna().sum()}, rango={dfA['PROF_EQ_m'].min()} a {dfA['PROF_EQ_m'].max()}")
    fondoA, resA = registro_fondo(
        dfA, estacion_col="ESTACION", fecha_col="FECHA_INICIO", prof_col="PROF_EQ_m",
        archivo="A",
        fondo_col="PROF_SECT_m",
        var_map={"TEMPERATURA_C": "temperatura_C",
                 "OXIG_ml_L": "oxigeno_ml_L",
                 "OXIG_mg_L": "oxigeno_mg_L",
                 "SALINIDAD_psu": "salinidad_psu"},
    )

    # --- Archivo B ---
    dfB = leer_archivo_b(ARCH_B)
    print(f"\nArchivo B leido: {dfB.shape}")
    print(f"  CODIGO: nula={dfB['CODIGO'].isna().sum()}, n_unicos={dfB['CODIGO'].nunique()}")
    print(f"  FECHA: nula={dfB['FECHA'].isna().sum()}")
    print(f"  PROFUNDIDAD_m: nula={dfB['PROFUNDIDAD_m'].isna().sum()}, rango={dfB['PROFUNDIDAD_m'].min()} a {dfB['PROFUNDIDAD_m'].max()}")
    fondoB, resB = registro_fondo(
        dfB, estacion_col="CODIGO", fecha_col="FECHA", prof_col="PROFUNDIDAD_m",
        archivo="B",
        fondo_col=None,  # marea roja: perfiles no llegan al fondo; sin dato de fondo en el archivo
        var_map={"TEMPERATURA_C": "temperatura_C",
                 "OXIGENO_ml_L": "oxigeno_ml_L",
                 "SALINIDAD_psu": "salinidad_psu"},
    )
    fondoB["oxigeno_mg_L"] = np.nan  # archivo B solo reporta oxigeno en ml/L

    # --- Profundidad de fondo para archivo B (marea roja) desde GEBCO_2026 ---
    # Los perfiles de marea roja no llegan al fondo (~50 m max) y el archivo
    # no trae profundidad de fondo. Se usa batimetria GEBCO_2026 por estacion.
    GBCO = BASE / "gebco_profundidades_marea_roja.csv"
    if GBCO.exists():
        gb = pd.read_csv(GBCO, dtype={"CODIGO": str})
        gb = gb.rename(columns={"CODIGO": "estacion_id"})
        gb["estacion_id"] = gb["estacion_id"].astype(str).str.strip()
        gb = gb[["estacion_id", "profundidad_fondo_m", "gebco_elevacion_m", "gebco_metodo"]]
        fondoB = fondoB.merge(gb, on="estacion_id", how="left", suffixes=("", "_gb"))
        # rellenar profundidad_fondo_m (NaN en fondoB) con el valor de GEBCO
        fondoB["profundidad_fondo_m"] = fondoB["profundidad_fondo_m"].fillna(
            fondoB["profundidad_fondo_m_gb"]
        )
        fondoB["profundidad_fondo_fuente"] = "GEBCO_2026"
        fondoB = fondoB.drop(columns=["profundidad_fondo_m_gb"])
    else:
        fondoB["profundidad_fondo_m"] = pd.NA
        fondoB["profundidad_fondo_fuente"] = "no_disponible"

    # --- Cobertura de estaciones: datos CTD vs CSV de zonas ---
    est_ctd_A = set(dfA["ESTACION"].dropna().astype(int).astype(str))
    est_ctd_B = set(dfB["CODIGO"].dropna().astype(str).str.strip())
    est_zona_A = set(zonas.loc[zonas.archivo == "A", "estacion_id"].astype(str).str.strip())
    est_zona_B = set(zonas.loc[zonas.archivo == "B", "estacion_id"].astype(str).str.strip())
    ctd_sin_zona_A = sorted(est_ctd_A - est_zona_A)
    ctd_sin_zona_B = sorted(est_ctd_B - est_zona_B)
    zona_sin_ctd_A = sorted(est_zona_A - est_ctd_A)
    zona_sin_ctd_B = sorted(est_zona_B - est_ctd_B)

    # Estaciones con filas en CTD pero sin registro de fondo (todas sus filas
    # tienen fecha invalida o profundidad invalida, p.ej. 'S/I').
    est_fondo_A = set(fondoA["estacion_id"])
    est_fondo_B = set(fondoB["estacion_id"])
    sin_fondo_A = sorted(est_ctd_A - est_fondo_A)
    sin_fondo_B = sorted(est_ctd_B - est_fondo_B)
    def motivo_sin_fondo(df, estacion_col, fecha_col, prof_col, ids):
        motivo = {}
        for i in ids:
            sub = df[df[estacion_col].astype(str).str.strip() == i]
            n_fecha = int(sub[fecha_col].isna().sum())
            n_prof = int(sub[prof_col].isna().sum())
            motivo[i] = f"filas={len(sub)}, fecha_invalida={n_fecha}/{len(sub)}, profundidad_invalida={n_prof}/{len(sub)}"
        return motivo
    motivo_A = motivo_sin_fondo(dfA, "ESTACION", "FECHA_INICIO", "PROF_EQ_m", sin_fondo_A)
    motivo_B = motivo_sin_fondo(dfB, "CODIGO", "FECHA", "PROFUNDIDAD_m", sin_fondo_B)

    # --- Union con zonas ---
    fondoA_z, sin_zona_A = unir_con_zonas(fondoA, zonas)
    fondoB_z, sin_zona_B = unir_con_zonas(fondoB, zonas)

    fondo = pd.concat([fondoA_z, fondoB_z], ignore_index=True)

    # Orden de columnas de salida
    cols_salida = ["archivo", "estacion_id", "fecha", "profundidad_fondo_m",
                   "profundidad_fondo_fuente",
                   "temperatura_C", "oxigeno_ml_L", "oxigeno_mg_L", "salinidad_psu",
                   "zona", "zona_tipo", "dist_km", "fuente"]
    fondo = fondo[cols_salida]

    # Guardar
    fondo.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"\nSalida guardada: {SALIDA} ({fondo.shape})")

    # --- Resumen ejecutivo ---
    nulos = fondo.isna().sum()
    print("\n===== RESUMEN EJECUTIVO =====")
    print(f"Filas totales salida: {len(fondo)}")
    print(f"  Archivo A: {resA['n_estacion_fecha']}  Archivo B: {resB['n_estacion_fecha']}")
    print(f"Rango fechas A: {fondoA['fecha'].min()} a {fondoA['fecha'].max()}")
    print(f"Rango fechas B: {fondoB['fecha'].min()} a {fondoB['fecha'].max()}")
    print(f"Estaciones sin zona match (en fondo): A={sin_zona_A} B={sin_zona_B} total={sin_zona_A+sin_zona_B}")
    print(f"Estaciones CTD sin zona asignada: A={len(ctd_sin_zona_A)} B={len(ctd_sin_zona_B)}")
    print(f"Estaciones con zona pero sin datos CTD: A={len(zona_sin_ctd_A)} B={len(zona_sin_ctd_B)} {zona_sin_ctd_B}")
    print("\nNulos por columna en salida:")
    print(nulos[nulos > 0] if (nulos > 0).any() else "  (ninguna)")
    print("\nNulos por archivo y variable (registro de fondo):")
    print(fondo.groupby("archivo")[["temperatura_C","oxigeno_ml_L","oxigeno_mg_L","salinidad_psu"]].apply(lambda x: x.isna().sum()))
    print("\nDetalle archivo A:", resA)
    print("Detalle archivo B:", resB)
    print(f"  Regla desempate B: {resB['regla_desempate']}")

    # Control de calidad: comparar n de salida vs suma de registros de fondo
    print(f"\nConsistencia: salida={len(fondo)} == fondoA={len(fondoA)}+fondoB={len(fondoB)} = {len(fondoA)+len(fondoB)}")

    return fondo, resA, resB


if __name__ == "__main__":
    fondo, resA, resB = main()
