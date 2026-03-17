from openai import OpenAI
import os
import json
from dotenv import load_dotenv

from config.settings import MODEL_NAME
from ai.prompts import heuristic_prompt

# Cargar variables del .env
load_dotenv()

# Crear cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def evaluate_heuristics(text):
    """
    Evalúa un sitio web según las 10 heurísticas de Nielsen.
    Devuelve un diccionario con H1-H10.
    """

    prompt = heuristic_prompt + "\n\nContenido del sitio:\n" + text

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Intentar parsear JSON
        scores = json.loads(content)

        return scores

    except json.JSONDecodeError:
        print("⚠️ Error interpretando JSON del modelo.")
        return {
            "H1": 3, "H2": 3, "H3": 3, "H4": 3, "H5": 3,
            "H6": 3, "H7": 3, "H8": 3, "H9": 3, "H10": 3
        }

    except Exception as e:
        print("⚠️ Error evaluando heurísticas:", e)
        return {
            "H1": 3, "H2": 3, "H3": 3, "H4": 3, "H5": 3,
            "H6": 3, "H7": 3, "H8": 3, "H9": 3, "H10": 3
        }