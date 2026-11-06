#!/usr/bin/env python3
"""Extrae de las salidas del pipeline todas las cifras que cita el informe.

Cada fila de cifras_informe.csv es una cifra publicable: clave, valor y la
salida de la que proviene. El informe Typst se escribe contra este archivo,
no contra la memoria de nadie.
"""
from pathlib import Path

import pandas as pd

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
OUT = BASE / "salidas" / "verificacion"
OUT.mkdir(parents=True, exist_ok=True)

filas = []


def add(clave, valor, fuente, nota=""):
    filas.append({"clave": clave, "valor": valor, "fuente": fuente, "nota": nota})


# ---------------------------------------------------------------- registro de fondo
fondo = pd.read_csv(BASE / "fondo_ctd_por_zona.csv", low_memory=False)
add("fondo.n_registros", len(fondo), "fondo_ctd_por_zona.csv")
add("fondo.n_estaciones", fondo["estacion_id"].nunique(), "fondo_ctd_por_zona.csv")
add("fondo.n_zonas", fondo["zona_mf"].nunique(), "fondo_ctd_por_zona.csv")
add("fondo.anio_min", int(fondo["fecha"].str[:4].min()), "fondo_ctd_por_zona.csv")
add("fondo.anio_max", int(fondo["fecha"].str[:4].max()), "fondo_ctd_por_zona.csv")
for arch, n in fondo.groupby("archivo").size().items():
    add(f"fondo.n_archivo_{arch}", n, "fondo_ctd_por_zona.csv")

for var, etiqueta in [
    ("temperatura_C", "temperatura"),
    ("oxigeno_ml_L", "oxigeno"),
    ("salinidad_psu", "salinidad"),
]:
    v = fondo[var].dropna()
    add(f"fondo.{etiqueta}.n", len(v), "fondo_ctd_por_zona.csv")
    add(f"fondo.{etiqueta}.media", round(float(v.mean()), 2), "fondo_ctd_por_zona.csv")
    add(f"fondo.{etiqueta}.mediana", round(float(v.median()), 2), "fondo_ctd_por_zona.csv")
    add(f"fondo.{etiqueta}.sd", round(float(v.std()), 2), "fondo_ctd_por_zona.csv")

# ---------------------------------------------------- análisis por zona (regenerado)
estado = pd.read_csv(BASE / "salidas/analisis_ambiental/estado_referencia_por_zona.csv")
tray = pd.read_csv(BASE / "salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv")
add("zonas.n_estado", len(estado), "salidas/analisis_ambiental/estado_referencia_por_zona.csv")
add("zonas.n_trayectorias", len(tray), "salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv")
add("zonas.n_anios_insuficientes", int((tray["temperatura_C_n_anos"] < 3).sum()),
    "salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv",
    "zonas con menos de 3 años: sin tendencia calculable")

for _, r in estado.iterrows():
    add(f"zona.{r.zona_mf}.n_registros", int(r.n_registros),
        "salidas/analisis_ambiental/estado_referencia_por_zona.csv")
    add(f"zona.{r.zona_mf}.n_estaciones", int(r.n_estaciones),
        "salidas/analisis_ambiental/estado_referencia_por_zona.csv")
    add(f"zona.{r.zona_mf}.temp_media", round(float(r.temperatura_C_media), 2),
        "salidas/analisis_ambiental/estado_referencia_por_zona.csv")
    add(f"zona.{r.zona_mf}.o2_media", round(float(r.oxigeno_ml_L_media), 2),
        "salidas/analisis_ambiental/estado_referencia_por_zona.csv")
    add(f"zona.{r.zona_mf}.sal_media", round(float(r.salinidad_psu_media), 2),
        "salidas/analisis_ambiental/estado_referencia_por_zona.csv")

# --------------------------------------------- tendencias del registro de fondo
sigtray = []
for var, etiqueta in [
    ("temperatura_C", "temperatura"),
    ("oxigeno_ml_L", "oxigeno"),
    ("salinidad_psu", "salinidad"),
]:
    for _, r in tray[tray[f"{var}_p_valor"] < 0.05].iterrows():
        sigtray.append({
            "zona": r.zona_mf, "variable": etiqueta,
            "pendiente": round(float(r[f"{var}_pendiente"]), 3),
            "p": round(float(r[f"{var}_p_valor"]), 4),
            "r2": round(float(r[f"{var}_r2"]), 2),
            "n_anos": int(r[f"{var}_n_anos"]),
        })
add("fondo.n_tendencias_sig", len(sigtray),
    "salidas/analisis_ambiental/trayectorias_cambio_por_zona.csv")
pd.DataFrame(sigtray).to_csv(OUT / "tendencias_fondo_significativas.csv", index=False)

# ------------------------------------------- perfiles: regional por profundidad
prof = pd.read_csv(BASE / "salidas/perfiles_procesados/perfiles_procesados.csv", low_memory=False)
profreg = pd.read_csv(BASE / "salidas/perfiles_procesados/resumen_regional_por_profundidad.csv")
add("perfiles.n_registros", len(prof), "salidas/perfiles_procesados/perfiles_procesados.csv")
add("perfiles.n_estaciones", prof["estacion_id"].nunique(), "perfiles_procesados.csv")
add("perfiles.n_zonas", prof["zona_mf"].nunique(), "perfiles_procesados.csv")
add("perfiles.n_profundidades", prof["profundidad_m"].nunique(), "perfiles_procesados.csv")
add("perfiles.prof_min", int(prof["profundidad_m"].min()), "perfiles_procesados.csv")
add("perfiles.prof_max", int(prof["profundidad_m"].max()), "perfiles_procesados.csv")

cuadro_prof = []
for p in [1, 10, 20, 30, 50, 100, 200, 300]:
    r = profreg[profreg["profundidad_m"] == p].iloc[0]
    cuadro_prof.append({
        "profundidad_m": p,
        "n_registros": int(r.n_registros),
        "temp_media": round(float(r.temperatura_C_media), 2),
        "o2_media": round(float(r.oxigeno_ml_L_media), 2),
        "sal_media": round(float(r.salinidad_psu_media), 2),
        "n_zonas": int(r.n_zonas),
    })
pd.DataFrame(cuadro_prof).to_csv(OUT / "cuadro_resumen_por_profundidad.csv", index=False)

# --------------------------------------------------- tendencias por profundidad
anom = pd.read_csv(BASE / "salidas/perfiles_procesados/tendencias_anomalias_por_profundidad.csv")
sig = anom[anom["p_valor"] < 0.05]
add("anomalias.n_sig_total", len(sig), "tendencias_anomalias_por_profundidad.csv")
for var, etiqueta in [("temperatura_C", "temperatura"), ("oxigeno_ml_L", "oxigeno"),
                      ("salinidad_psu", "salinidad")]:
    add(f"anomalias.n_sig_{etiqueta}", int((sig["variable"] == var).sum()),
        "tendencias_anomalias_por_profundidad.csv")

serie = pd.read_csv(BASE / "salidas/analisis_serie_tiempo/resumen_tendencias_significativas.csv")
add("series.n_sig_total", len(serie), "resumen_tendencias_significativas.csv")
add("series.n_zonas", serie["zona_mf"].nunique(), "resumen_tendencias_significativas.csv")
add("series.n_profundidades", serie["profundidad_m"].nunique(), "resumen_tendencias_significativas.csv")
for var, etiqueta in [("temperatura_C", "temperatura"), ("oxigeno_ml_L", "oxigeno"),
                      ("salinidad_psu", "salinidad")]:
    d = serie[serie["variable"] == var]
    add(f"series.n_sig_{etiqueta}", len(d), "resumen_tendencias_significativas.csv")
    add(f"series.pendiente_media_{etiqueta}", round(float(d["pendiente"].mean()), 3),
        "resumen_tendencias_significativas.csv")
    add(f"series.decada_media_{etiqueta}", round(float(d["cambio_decada"].mean()), 2),
        "resumen_tendencias_significativas.csv")
    add(f"series.r2_medio_{etiqueta}", round(float(d["r2"].mean()), 3),
        "resumen_tendencias_significativas.csv")
    add(f"series.p_min_{etiqueta}", round(float(d["p_valor"].min()), 4),
        "resumen_tendencias_significativas.csv")

est = pd.read_csv(BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv")
lat = est.groupby("zona_mf")["lat"].mean()

# top 5 por variable, con el signo que corresponda
tops = []
for var, etiqueta in [("temperatura_C", "temperatura"), ("oxigeno_ml_L", "oxigeno"),
                      ("salinidad_psu", "salinidad")]:
    d = serie[serie["variable"] == var]
    d = d.reindex(d["pendiente"].abs().sort_values(ascending=False).index).head(5)
    for _, r in d.iterrows():
        tops.append({
            "variable": etiqueta, "zona": r.zona_mf, "profundidad_m": r.profundidad_m,
            "pendiente": round(float(r.pendiente), 2),
            "cambio_decada": round(float(r.cambio_decada), 2),
            "p": round(float(r.p_valor), 3), "r2": round(float(r.r2), 3),
            "n_anos": int(r.n_anos),
            "_lat": float(lat[r.zona_mf]),
        })
tops_df = pd.DataFrame(tops).sort_values(["variable", "_lat"], ascending=[True, False]).drop(columns="_lat")
tops_df.to_csv(OUT / "top_tendencias_por_variable.csv", index=False)

# --------------------------------------------------------- tabla de tendencias
# Filas seleccionadas por bloques coherentes, no por ranking: así la tabla del
# informe no repite el mismo proceso con profundidades contiguas.
seleccion = [
    ("salinidad_psu", "Aysen", [44.0, 56.0, 239.0, 247.0, 248.0, 251.0]),
    ("salinidad_psu", "Butachauques", [285.0, 295.0, 304.0]),
    ("temperatura_C", "Quellon", [3.0, 10.0, 22.0]),
]
filas_sel = []
for var, zona, profs in seleccion:
    d = anom[(anom["zona_mf"] == zona) & (anom["variable"] == var)]
    for p in profs:
        r = d[d["profundidad_m"] == p]
        if r.empty:
            continue
        r = r.iloc[0]
        filas_sel.append({
            "zona": zona, "variable": var, "profundidad_m": p,
            "tendencia": round(float(r.tendencia_anual), 3),
            "p": round(float(r.p_valor), 3), "r2": round(float(r.r2), 3),
            "n_anos": int(r.n_anos),
            "_lat": float(lat[zona]),
        })
pd.DataFrame(filas_sel).sort_values(["_lat", "profundidad_m"], ascending=[False, True]).drop(columns="_lat").to_csv(
    OUT / "tendencias_profundidad_seleccion.csv", index=False)
add("anomalias.n_filas_tabla", len(filas_sel), "tendencias_profundidad_seleccion.csv")

df = pd.DataFrame(filas).sort_values("clave")
df.to_csv(OUT / "cifras_informe.csv", index=False)
print(df.to_string(index=False))
print(f"\n{len(df)} cifras -> {OUT/'cifras_informe.csv'}")
