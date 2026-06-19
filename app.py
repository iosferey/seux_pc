from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import glob
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

from seuxpc.modules.pipeline.engine import SEUXPC
from seuxpc.utils.io import save_result_json
from seuxpc.utils.export_csv import export_summary_csv

app = FastAPI()


class RequestModel(BaseModel):
    url: str
    country: Optional[str] = None


class BatchRequestModel(BaseModel):
    urls: List[str]
    country: Optional[str] = None


@app.get("/countries")
def get_countries():
    from seuxpc.config.hofstede import HOFSTEDE
    list_countries = []
    for code, data in HOFSTEDE.items():
        list_countries.append({
            "code": code,
            "name": data.get("country", code)
        })
    list_countries.sort(key=lambda x: x["name"])
    return list_countries


@app.get("/history")
def get_history():
    out_dir = "outputs"
    if not os.path.exists(out_dir):
        return []

    files = glob.glob(os.path.join(out_dir, "*.json"))
    history_list = []

    for f in files:
        filename = os.path.basename(f)
        try:
            mtime = os.path.getmtime(f)
            date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Infección de URL si no existe
            url = data.get("url")
            if not url:
                # El nombre de archivo es dominio_YYYYMMDD_HHMMSS.json
                parts = filename.split("_")
                if len(parts) >= 3:
                    url = "https://" + "_".join(parts[:-2])
                else:
                    url = "https://" + filename.replace(".json", "")

            history_list.append({
                "filename": filename,
                "url": url,
                "date": date_str,
                "ICH": data.get("ICH"),
                "IAC": data.get("IAC"),
                "IVS": data.get("IVS"),
                "Brecha": data.get("Brecha"),
                "pais_origen": data.get("pais_origen"),
                "pais_origen_nombre": data.get("pais_origen_nombre"),
                "pais_objetivo": data.get("pais_objetivo"),
                "pais_objetivo_nombre": data.get("pais_objetivo_nombre"),
                "mtime": mtime
            })
        except Exception as e:
            print(f"Error cargando archivo de historial {filename}: {e}")

    # Ordenar por fecha de modificación, más recientes primero
    history_list.sort(key=lambda x: x["mtime"], reverse=True)
    return history_list


@app.get("/history/{filename}")
def get_history_file(filename: str):
    # Sanitizar nombre de archivo para evitar path traversal
    clean_filename = os.path.basename(filename)
    path = os.path.join("outputs", clean_filename)
    if not os.path.exists(path):
        return Response(status_code=404, content="Archivo no encontrado")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Inyectar url si no existe
        if "url" not in data:
            parts = clean_filename.split("_")
            if len(parts) >= 3:
                data["url"] = "https://" + "_".join(parts[:-2])
            else:
                data["url"] = "https://" + clean_filename.replace(".json", "")

        # Inyectar perfiles si no existen para compatibilidad del gráfico de radar
        from seuxpc.config.hofstede import HOFSTEDE
        if "pais_origen_profile" not in data:
            origin_code = data.get("pais_origen", "USA")
            data["pais_origen_profile"] = HOFSTEDE.get(origin_code, {})
        if "pais_objetivo_profile" not in data:
            target_code = data.get("pais_objetivo", "MEX")
            data["pais_objetivo_profile"] = HOFSTEDE.get(target_code, {})

        return data
    except Exception as e:
        return Response(status_code=500, content=f"Error leyendo archivo: {str(e)}")


@app.post("/analyze")
def analyze(data: RequestModel):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return Response(status_code=500, content="No se encontró la variable de entorno OPENAI_API_KEY")

    normalized_url = data.url.strip()
    if not normalized_url.startswith("http"):
        normalized_url = "https://" + normalized_url

    model = SEUXPC(
        url=normalized_url,
        target_country=data.country,
        api_key=api_key,
        enable_recommendations=True
    )

    result = model.run()
    result["url"] = normalized_url

    # Inyectar perfiles de dimensiones culturales
    from seuxpc.config.hofstede import HOFSTEDE
    result["pais_origen_profile"] = HOFSTEDE.get(result.get("pais_origen"), {})
    result["pais_objetivo_profile"] = HOFSTEDE.get(result.get("pais_objetivo"), {})

    # Guardar en outputs/ para historial
    save_result_json(result, normalized_url)

    return result


@app.post("/batch-analyze")
def batch_analyze(data: BatchRequestModel):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return Response(status_code=500, content="No se encontró la variable de entorno OPENAI_API_KEY")

    results = []
    target_country = None if data.country and data.country.lower() == "auto" else data.country

    for url in data.urls:
        if not url.strip():
            continue
        normalized_url = url.strip()
        if not normalized_url.startswith("http"):
            normalized_url = "https://" + normalized_url

        try:
            model = SEUXPC(
                url=normalized_url,
                target_country=target_country,
                api_key=api_key,
                enable_recommendations=False
            )
            result = model.run()
            result["url"] = normalized_url

            # Guardar JSON individual
            save_result_json(result, normalized_url)
            results.append(result)
        except Exception as e:
            print(f"Error procesando batch URL {normalized_url}: {e}")

    if results:
        csv_path = export_summary_csv(results)
        summary_filename = os.path.basename(csv_path)
    else:
        summary_filename = None

    return {
        "processed": len(results),
        "results": [
            {
                "url": r.get("url"),
                "ICH": r.get("ICH"),
                "IAC": r.get("IAC"),
                "IVS": r.get("IVS"),
                "Brecha": r.get("Brecha"),
                "pais_origen_nombre": r.get("pais_origen_nombre"),
                "pais_objetivo_nombre": r.get("pais_objetivo_nombre")
            } for r in results
        ],
        "summary_csv": summary_filename
    }


@app.get("/download-summary/{filename}")
def download_summary(filename: str):
    clean_filename = os.path.basename(filename)
    path = os.path.join("outputs", clean_filename)
    if not os.path.exists(path) or not clean_filename.startswith("summary_"):
        return Response(status_code=404, content="Archivo no encontrado")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={clean_filename}"}
    )


# ---------------------------
# SERVIR ARCHIVOS ESTÁTICOS
# ---------------------------

@app.get("/")
def get_index():
    path = os.path.join("static", "index.html")
    if not os.path.exists(path):
        return HTMLResponse(content="<h1>Frontend no encontrado. Crea static/index.html</h1>", status_code=404)
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/static/{filepath:path}")
def get_static(filepath: str):
    safe_path = os.path.join("static", os.path.normpath(filepath))
    if not safe_path.startswith("static/") and not safe_path.startswith("static\\"):
        return Response(status_code=403, content="Acceso denegado")
    if not os.path.isfile(safe_path):
        return Response(status_code=404, content="Archivo no encontrado")

    mime_types = {
        ".css": "text/css",
        ".js": "application/javascript",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".ico": "image/x-icon"
    }
    _, ext = os.path.splitext(safe_path)
    content_type = mime_types.get(ext.lower(), "text/plain")

    with open(safe_path, "rb") as f:
        return Response(content=f.read(), media_type=content_type)

