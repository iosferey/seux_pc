import csv
import os
from datetime import datetime

def export_summary_csv(results, path=None):
    os.makedirs("outputs", exist_ok=True)

    if path is None:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"outputs/summary_{ts}.csv"

    keys = ["ICH", "IAC", "IVS", "Brecha",
            "transferencia_cultural", "pais_origen", "pais_origen_nombre",
            "pais_objetivo", "pais_objetivo_nombre", "F_conexion_narrativa_simbolica"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for r in results:
            row = {k: r.get(k) for k in keys[:-1]}  # All keys except F
            # Extract F from heuristics and normalize to 0-1
            heuristics = r.get("heuristics", {})
            f_raw = heuristics.get("F_conexion_narrativa_simbolica", 3)  # default 3 (neutral)
            row["F_conexion_narrativa_simbolica"] = max(0.0, min(1.0, (float(f_raw) - 1.0) / 4.0))
            writer.writerow(row)

    return path
