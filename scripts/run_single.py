import os
import sys
import argparse
import importlib
import json

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


def get_args():
    parser = argparse.ArgumentParser(
        description="Ejecuta el modelo SEUX-PC para una URL"
    )

    parser.add_argument(
        "--url",
        type=str,
        help="URL del sitio a analizar"
    )

    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="País objetivo por código o nombre; si se omite, se infiere"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="No guardar resultado en JSON"
    )

    return parser.parse_args()


def main():
    args = get_args()

    # ---------------------------
    # 1. OBTENER URL
    # ---------------------------
    url = args.url

    if not url:
        url = input("🌐 Ingresa la URL a analizar: ").strip()

    if not url.startswith("http"):
        url = "https://" + url

    # ---------------------------
    # 2. API KEY
    # ---------------------------
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("No se encontró OPENAI_API_KEY")

    # ---------------------------
    # 3. EJECUTAR MODELO
    # ---------------------------
    print("\n🚀 Ejecutando análisis...\n")

    model = SEUXPC(
        url=url,
        target_country=args.country,
        api_key=api_key
    )

    result = model.run()

    # ---------------------------
    # 4. MOSTRAR RESULTADO
    # ---------------------------
    print("\n📊 RESULTADO:\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # ---------------------------
    # 5. GUARDAR
    # ---------------------------
    if not args.no_save:
        path = save_result_json(result, url)
        print(f"\n💾 Guardado en: {path}")


if __name__ == "__main__":
    main()
