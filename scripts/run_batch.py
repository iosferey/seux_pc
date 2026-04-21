import os
import time
import random
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

TARGET_COUNTRY = "MX"
API_KEY = os.getenv("OPENAI_API_KEY")

def run_batch():
    results = []

    for i, url in enumerate(URLS, start=1):
        print(f"\n[{i}/{len(URLS)}] Procesando: {url}")

        try:
            model = SEUXPC(
                url=url,
                target_country=TARGET_COUNTRY,
                api_key=API_KEY
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
    run_batch()