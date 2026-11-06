#!/usr/bin/env python3
from pathlib import Path

import pandas as pd

BASE = Path("/home/rfvera/Documentos/IFOP/SEGUIMIENTO/objetivo_4")
OUT = BASE / "salidas" / "verificacion" / "zonas_estaciones.csv"

e = pd.read_csv(BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv")
est = pd.read_csv(BASE / "estaciones_CTD_con_ZONA_MACROFAUNA.csv")
lat = est.groupby("zona_mf")["lat"].mean()

rows = []
for zona, g in e.groupby("zona_mf"):
    ids = sorted(g["estacion_id"].unique(), key=lambda x: str(x))
    rows.append({
        "zona": zona,
        "n": len(ids),
        "estaciones": ", ".join(str(i) for i in ids),
        "_lat": float(lat[zona]),
    })
df = pd.DataFrame(rows).sort_values("_lat", ascending=False).drop(columns="_lat")
df.to_csv(OUT, index=False)
print("->", OUT, "(", len(df), "zonas )")