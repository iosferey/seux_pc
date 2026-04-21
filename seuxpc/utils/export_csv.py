import csv
import os

def export_summary_csv(results, path="outputs/summary.csv"):
    os.makedirs("outputs", exist_ok=True)

    keys = ["ICH", "IAC", "IVS", "Brecha",
            "transferencia_cultural", "pais_origen", "pais_objetivo"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for r in results:
            row = {k: r.get(k) for k in keys}
            writer.writerow(row)

    return path