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
            "pais_objetivo", "pais_objetivo_nombre"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for r in results:
            row = {k: r.get(k) for k in keys}
            writer.writerow(row)

    return path
