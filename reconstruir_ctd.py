"""
reconstruir_ctd.py
Agente DATA - IFOP Seguimiento (objetivo_4)

Reconstruye el registro de fondo CTD desde los dos archivos originales
aplicando el procedimiento estándar de procesamiento de perfiles CTD:

1. Lectura de archivos originales (solo lectura, nunca sobrescribir)
2. Trimming: remover datos de superficie/calibración y fase de equilibrio
3. Despiking: eliminar valores atípicos por variable
4. Bin averaging: promediar en bins de 1 metro de profundidad
5. Registro de fondo: tomar la medición a la profundidad máxima por estación×fecha
6. Unión con zonas de macrofauna (zona_mf)

Entradas (solo lectura):
  - Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx (archivo A)
  - datos CTD - marea roja.xlsx (archivo B)
  - estaciones_CTD_con_ZONA_MACROFAUNA.csv

Salida:
  - fondo_ctd_por_zona.csv (reconstruido)

Reglas clave:
  - Nunca sobrescribir .xlsx fuentes
  - Archivo A: FLAG_BOOL==0 = superficie/calibración, se descarta.
                Profundidades son enteros (1m, 2m...), ya binneadas.
                Nutrientes/clorofila de botella se dejan como están (no se promedian).
  - Archivo B: Datos de alta frecuencia, necesitan trimming + bin averaging 1m.
               No hay FLAG_BOOL, se asume todo el perfil es válido (downcast).
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import signal

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
ARCH_A = BASE / "Compilacion_BD_CTD_SEGUIMIENTO_2019-2025.xlsx"
ARCH_B = BASE / "datos CTD - marea roja.xlsx"
ZONAS_MF = BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv"
GEBCO_PROF = BASE / "gebco_profundidades_marea_roja.csv"
SALIDA = BASE / "fondo_ctd_por_zona.csv"

VARIABLES_CTD = ["temperatura_C", "oxigeno_ml_L", "salinidad_psu"]

# ---------------------------------------------------------------------------
# 1. Lectura archivo A (seguimiento 2019-2025)
# ---------------------------------------------------------------------------
def leer_archivo_a(path: Path) -> pd.DataFrame:
    """Lee la hoja de datos del archivo A.
    Filas 0-19 = metadatos, fila 20 (0-indexed) = encabezado, datos desde fila 21.
    """
    raw = pd.read_excel(path, sheet_name="Base de Datos CTD2019-2025_IFOP", header=None)
    if raw.shape[0] <= 21:
        raise ValueError("Archivo A no tiene el encabezado esperado en la fila 20")
    header = raw.iloc[20].tolist()
    df = raw.iloc[21:].copy()
    df.columns = header

    # Renombrar por posición para evitar columna sin nombre (col 7) y duplicado ESTACION (col 28)
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
        raise ValueError("Esperaba {} columnas, leí {}".format(len(nombres), df.shape[1]))
    df.columns = nombres

    # Tipos
    df["ESTACION"] = pd.to_numeric(df["ESTACION"], errors="coerce")
    df["FECHA_INICIO"] = pd.to_datetime(df["FECHA_INICIO"], errors="coerce")
    df["PROF_EQ_m"] = pd.to_numeric(df["PROF_EQ_m"], errors="coerce")
    df["PROF_SECT_m"] = pd.to_numeric(df["PROF_SECT_m"], errors="coerce")
    for c in ["TEMPERATURA_C", "OXIG_ml_L", "OXIG_mg_L", "SALINIDAD_psu"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# 2. Lectura archivo B (marea roja)
# ---------------------------------------------------------------------------
def leer_archivo_b(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Datos CTD", header=0)

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
# 3. Trimming: remover superficie / calibración
# ---------------------------------------------------------------------------
def trim_archivo_a(df: pd.DataFrame) -> pd.DataFrame:
    """Archivo A: FLAG_BOOL==0 marca datos de superficie/calibración.
    Se descarta. Solo quedan FLAG_BOOL==1 (perfil CTD válido).
    Además se descarta profundidad 0 (en el aire).
    """
    n_antes = len(df)
    df = df[df["FLAG_BOOL"] == 1].copy()
    df = df[df["PROF_EQ_m"] > 0].copy()
    despues = len(df)
    print("  Archivo A trimming: {} filas -> {} filas (descartadas {})".format(n_antes, despues, n_antes - despues))
    return df


def trim_archivo_b(df: pd.DataFrame, prof_min: float = 0.5) -> pd.DataFrame:
    """Archivo B: no tiene FLAG_BOOL. Se descartan profundidades < prof_min m
    (datos en el aire / calibración en superficie).
    """
    n_antes = len(df)
    df = df[df["PROFUNDIDAD_m"] >= prof_min].copy()
    despues = len(df)
    print("  Archivo B trimming: {} filas -> {} filas (profundidad < {} m descartadas)".format(n_antes, despues, prof_min))
    return df


# ---------------------------------------------------------------------------
# 4. Despiking: eliminar valores atípicos por grupo (estación×fecha)
# ---------------------------------------------------------------------------
def despikear_grupo(sub: pd.DataFrame, prof_col: str, var_cols: list) -> pd.DataFrame:
    """Elimina valores atípicos usando regla del IQR por variable dentro de cada grupo.
    Los valores atípicos se marcan como NaN, no se eliminan la fila.
    """
    resultado = sub.copy()
    for var in var_cols:
        if var not in sub.columns:
            continue
        valores = sub[var].dropna()
        if len(valores) < 4:
            continue
        q1 = valores.quantile(0.25)
        q3 = valores.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        limite_inf = q1 - 3.0 * iqr
        limite_sup = q3 + 3.0 * iqr
        mascara = (sub[var] < limite_inf) | (sub[var] > limite_sup)
        resultado.loc[mascara, var] = np.nan
    return resultado


# ---------------------------------------------------------------------------
# 5. Bin averaging: promediar en bins de 1 metro
# ---------------------------------------------------------------------------
def bin_average(df: pd.DataFrame, prof_col: str, var_cols: list, bin_size: float = 1.0,
                id_cols: list | None = None) -> pd.DataFrame:
    """Promedia variables en bins de profundidad de bin_size metros.
    Devuelve un DataFrame con una fila por bin (profundidad del centro del bin).
    id_cols: columnas adicionales a copiar (ej. estación, fecha).
    """
    filas = []
    for prof_bin, sub in df.groupby(pd.cut(df[prof_col], bins=np.arange(df[prof_col].min(), df[prof_col].max() + bin_size, bin_size))):
        if pd.isna(prof_bin.left):
            continue
        prof_centro = prof_bin.mid
        fila = {prof_col: prof_centro}
        if id_cols:
            for ic in id_cols:
                fila[ic] = sub[ic].iloc[0]
        for var in var_cols:
            vals = sub[var].dropna()
            fila[var] = float(vals.mean()) if len(vals) > 0 else np.nan
        filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# 6. Registro de fondo por estación×fecha
# ---------------------------------------------------------------------------
def registro_fondo_por_grupo(df: pd.DataFrame, estacion_col: str, fecha_col: str,
                             prof_col: str, archivo: str,
                             fondo_col: str | None = None,
                             var_cols: list | None = None) -> pd.DataFrame:
    """Para cada (estación, fecha):
      - Selecciona la fila de profundidad máxima (registro de fondo)
      - Las variables se toman de esa fila
    var_cols: nombres originales de las columnas de variables en df.
    """
    val = df.dropna(subset=[estacion_col, fecha_col, prof_col]).copy()
    if len(val) == 0:
        return pd.DataFrame(), {"archivo": archivo, "n_estacion_fecha": 0}

    # Índice de la profundidad máxima por grupo
    idx = val.groupby([estacion_col, fecha_col])[prof_col].idxmax()
    fondo = val.loc[idx].copy()

    # Profundidad de fondo
    if fondo_col is not None and fondo_col in val.columns:
        fondo_map = val.groupby([estacion_col, fecha_col])[fondo_col].max().rename("profundidad_fondo_m")
        fondo = fondo.merge(fondo_map, on=[estacion_col, fecha_col], how="left")
        fondo_fuente = fondo_col
    else:
        fondo["profundidad_fondo_m"] = pd.NA
        fondo_fuente = None

    out = pd.DataFrame({
        "archivo": archivo,
        "estacion_id": fondo[estacion_col].astype(str),
        "fecha": fondo[fecha_col],
        "profundidad_fondo_m": fondo["profundidad_fondo_m"],
        "profundidad_fondo_fuente": fondo_fuente if fondo_fuente else "no_disponible",
    })
    if var_cols:
        # Mapear nombres originales a estándar de salida
        mapeo = {
            "TEMPERATURA_C": "temperatura_C",
            "OXIG_ml_L": "oxigeno_ml_L",
            "OXIGENO_ml_L": "oxigeno_ml_L",
            "SALINIDAD_psu": "salinidad_psu",
        }
        for var in var_cols:
            if var in fondo.columns:
                out[mapeo.get(var, var)] = fondo[var].values

    resumen = {
        "archivo": archivo,
        "n_estacion_fecha": len(fondo),
    }
    return out, resumen


# ---------------------------------------------------------------------------
# 7. Unión con zonas
# ---------------------------------------------------------------------------
def unir_con_zonas(fondo: pd.DataFrame, zonas: pd.DataFrame) -> pd.DataFrame:
    zonas_u = zonas[["archivo", "estacion_id", "zona_mf", "acs_mf", "dist_km"]].copy()
    zonas_u["estacion_id"] = zonas_u["estacion_id"].astype(str).str.strip()
    fondo["estacion_id"] = fondo["estacion_id"].astype(str).str.strip()

    merged = fondo.merge(zonas_u, on=["archivo", "estacion_id"], how="left")
    n_sin_zona = int(merged["zona_mf"].isna().sum())
    print("Estaciones sin zona_mf: {}".format(n_sin_zona))
    return merged, n_sin_zona


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    zonas = pd.read_csv(ZONAS_MF, dtype={"estacion_id": str})
    print("Zonas cargadas: {} filas".format(zonas.shape[0]))

    # --- Archivo A ---
    print("\n=== Archivo A ===")
    dfA = leer_archivo_a(ARCH_A)
    print("Leído: {} filas".format(dfA.shape[0]))
    dfA = trim_archivo_a(dfA)

    # Nombres de columnas del archivo A (según el encabezado del xlsx)
    VAR_A = ["TEMPERATURA_C", "OXIG_ml_L", "SALINIDAD_psu"]

    # Despiking por grupo (estación×fecha)
    print("Despiking archivo A...")
    VAR_A_DESPIKE = VAR_A + ["DENSIDAD_sigma_t"]
    lista_A = []
    for (est, fec), sub in dfA.groupby(["ESTACION", "FECHA_INICIO"]):
        lista_A.append(despikear_grupo(sub.reset_index(drop=True), "PROF_EQ_m", VAR_A_DESPIKE))
    dfA = pd.concat(lista_A, ignore_index=True)

    # Lookup de PROF_SECT_m por grupo (máximo por estación×fecha)
    print("Lookup PROF_SECT_m archivo A...")
    prof_sect_lookup = dfA.groupby(["ESTACION", "FECHA_INICIO"])["PROF_SECT_m"].max().reset_index()

    # Bin averaging por 1 metro (ya está a enteros, pero aseguramos)
    print("Bin averaging archivo A (1m)...")
    lista_A_bin = []
    for (est, fec), sub in dfA.groupby(["ESTACION", "FECHA_INICIO"]):
        sub = sub.copy()
        sub["ESTACION"] = est
        sub["FECHA_INICIO"] = fec
        lista_A_bin.append(bin_average(sub, "PROF_EQ_m", VAR_A, bin_size=1.0,
                                       id_cols=["ESTACION", "FECHA_INICIO"]))
    dfA_bin = pd.concat(lista_A_bin, ignore_index=True)

    # Agregar PROF_SECT_m al bineado
    dfA_bin = dfA_bin.merge(prof_sect_lookup, on=["ESTACION", "FECHA_INICIO"], how="left")

    fondoA, resA = registro_fondo_por_grupo(
        dfA_bin, estacion_col="ESTACION", fecha_col="FECHA_INICIO",
        prof_col="PROF_EQ_m", archivo="A", fondo_col="PROF_SECT_m",
        var_cols=VAR_A,
    )
    print("Archivo A: {} registros de fondo".format(resA["n_estacion_fecha"]))

    # --- Archivo B ---
    print("\n=== Archivo B ===")
    dfB = leer_archivo_b(ARCH_B)
    print("Leído: {} filas".format(dfB.shape[0]))
    dfB = trim_archivo_b(dfB, prof_min=0.5)

    # Despiking por grupo
    print("Despiking archivo B...")
    lista_B = []
    for (cod, fec), sub in dfB.groupby(["CODIGO", "FECHA"]):
        lista_B.append(despikear_grupo(sub.reset_index(drop=True), "PROFUNDIDAD_m", ["TEMPERATURA_C", "OXIGENO_ml_L", "SALINIDAD_psu"]))
    dfB = pd.concat(lista_B, ignore_index=True)

    # Nombres de columnas del archivo B (después del rename en leer_archivo_b)
    VAR_B = ["TEMPERATURA_C", "OXIGENO_ml_L", "SALINIDAD_psu"]

    # Bin averaging por 1 metro
    print("Bin averaging archivo B (1m)...")
    lista_B_bin = []
    for (cod, fec), sub in dfB.groupby(["CODIGO", "FECHA"]):
        sub = sub.copy()
        sub["CODIGO"] = cod
        sub["FECHA"] = fec
        lista_B_bin.append(bin_average(sub, "PROFUNDIDAD_m", VAR_B, bin_size=1.0,
                                       id_cols=["CODIGO", "FECHA"]))
    dfB_bin = pd.concat(lista_B_bin, ignore_index=True)

    fondoB, resB = registro_fondo_por_grupo(
        dfB_bin, estacion_col="CODIGO", fecha_col="FECHA",
        prof_col="PROFUNDIDAD_m", archivo="B", fondo_col=None,
        var_cols=VAR_B,
    )
    print("Archivo B: {} registros de fondo".format(resB["n_estacion_fecha"]))

    # --- Integrar profundidades GEBCO para archivo B ---
    print("Integrando profundidades GEBCO_2026 para archivo B...")
    if GEBCO_PROF.exists():
        gb = pd.read_csv(GEBCO_PROF, dtype={"CODIGO": str})
        gb = gb.rename(columns={"CODIGO": "estacion_id", "profundidad_fondo_m": "gebco_prof_m"})
        gb["estacion_id"] = gb["estacion_id"].astype(str).str.strip()
        fondoB = fondoB.merge(gb[["estacion_id", "gebco_prof_m"]], on="estacion_id", how="left")
        # Rellenar profundidad_fondo_m con GEBCO donde sea NaN
        fondoB["profundidad_fondo_m"] = fondoB["profundidad_fondo_m"].fillna(fondoB["gebco_prof_m"])
        fondoB.loc[fondoB["profundidad_fondo_fuente"] == "no_disponible", "profundidad_fondo_fuente"] = "GEBCO_2026"
        fondoB = fondoB.drop(columns=["gebco_prof_m"])
        print("  {} registros de archivo B con profundidad GEBCO".format(fondoB["profundidad_fondo_m"].notna().sum()))
    else:
        print("  ADVERTENCIA: archivo GEBCO no encontrado, profundidades de B quedan NaN")

    # --- Combinar ---
    fondo = pd.concat([fondoA, fondoB], ignore_index=True)

    # Mapear nombres de variables a estándar de salida
    fondo = fondo.rename(columns={
        "TEMPERATURA_C": "temperatura_C",
        "OXIGENO_ml_L": "oxigeno_ml_L",
        "SALINIDAD_psu": "salinidad_psu",
    })

    # --- Unión con zonas ---
    fondo_z, n_sin_zona = unir_con_zonas(fondo, zonas)

    # Orden de columnas
    cols_salida = ["archivo", "estacion_id", "fecha", "profundidad_fondo_m",
                   "profundidad_fondo_fuente", "temperatura_C", "oxigeno_ml_L", "salinidad_psu",
                   "zona_mf", "acs_mf", "dist_km"]
    fondo_z = fondo_z[cols_salida]

    # Guardar
    fondo_z.to_csv(SALIDA, index=False, encoding="utf-8")
    print("\n=== Salida guardada: {} ({} filas) ===".format(SALIDA, fondo_z.shape))
    print("  Archivo A: {} registros".format(resA["n_estacion_fecha"]))
    print("  Archivo B: {} registros".format(resB["n_estacion_fecha"]))
    print("  Total: {} registros".format(len(fondo_z)))

    return fondo_z


if __name__ == "__main__":
    fondo = main()
