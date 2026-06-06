import argparse
import csv
import os
import time
import random
import sys
import importlib

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

dotenv_spec = importlib.util.find_spec("dotenv")
if dotenv_spec is not None:
    dotenv_module = importlib.import_module("dotenv")
    dotenv_module.load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from seuxpc.modules.pipeline.engine import SEUXPC
from seuxpc.utils.io import save_result_json
from seuxpc.utils.export_csv import export_summary_csv

URLS = [
    "https://stripe.com",
    "https://airbnb.com",
    "https://apple.com",
    "https://nike.com",
    "https://spotify.com"
]

API_KEY = os.getenv("OPENAI_API_KEY")


def get_args():
    parser = argparse.ArgumentParser(
        description="Ejecuta el modelo SEUX-PC para un lote de URLs"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="CSV con una columna 'url'. Filas vacias o con # se ignoran."
    )
    parser.add_argument(
        "--country",
        type=str,
        default="MEX",
        help="Pais objetivo para todo el lote. Usa 'auto' para inferirlo por sitio."
    )
    return parser.parse_args()


def load_urls_from_csv(path):
    urls = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames or "url" not in reader.fieldnames:
            raise ValueError("El CSV debe incluir una columna llamada 'url'")

        for row in reader:
            url = (row.get("url") or "").strip()

            if not url or url.startswith("#"):
                continue

            if not url.startswith("http"):
                url = "https://" + url

            urls.append(url)

    return urls


def run_batch(urls, target_country="MEX"):
    results = []
    target_country = None if str(target_country).lower() == "auto" else target_country

    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{len(urls)}] Procesando: {url}")

        try:
            model = SEUXPC(
                url=url,
                target_country=target_country,
                api_key=API_KEY,
                enable_recommendations=False
            )

            result = model.run()

            save_result_json(result, url)
            results.append(result)

            print("✔ OK")

        except Exception as e:
            print("❌ Error:", e)

        # evita saturar API / navegador
        time.sleep(random.uniform(1.5, 3.5))

    csv_path = export_summary_csv(results)
    print("CSV generado:", csv_path)

if __name__ == "__main__":
    args = get_args()
    urls = load_urls_from_csv(args.csv) if args.csv else URLS
    run_batch(urls, target_country=args.country)
