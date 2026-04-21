import json
import re
from openai import OpenAI

from seuxpc.config.prompts import LLM_PROMPT_TEMPLATE
from seuxpc.config.settings import OPENAI_MODEL, TEMPERATURE, MAX_HTML_CHARS


class LLMHeuristicEvaluator:

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API key de OpenAI no proporcionada")

        self.client = OpenAI(api_key=api_key)

    def evaluate(self, html):

        # ---------------------------
        # 1. LIMPIAR / RECORTAR HTML
        # ---------------------------
        html_clean = html.strip().replace("\n", " ")
        html_trimmed = html_clean[:MAX_HTML_CHARS]

        # ---------------------------
        # 2. GENERAR PROMPT
        # ---------------------------
        prompt = LLM_PROMPT_TEMPLATE.replace("{html}", html_trimmed)

        # ---------------------------
        # 3. LLAMADA AL MODELO
        # ---------------------------
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=TEMPERATURE,
                response_format={"type": "json_object"},  # 🔥 clave para estabilidad
                messages=[
                    {"role": "system", "content": "Eres un experto en UX."},
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as e:
            print("❌ Error al llamar OpenAI:", e)
            raise

        # ---------------------------
        # 4. OBTENER CONTENIDO
        # ---------------------------
        content = response.choices[0].message.content

        if not content:
            raise ValueError("Respuesta vacía del LLM")

        # ---------------------------
        # 5. PARSEO JSON (modo robusto)
        # ---------------------------
        try:
            return json.loads(content)

        except json.JSONDecodeError:

            # fallback: buscar JSON dentro del texto
            match = re.search(r'\{.*\}', content, re.DOTALL)

            if not match:
                print("⚠️ Respuesta inválida del LLM:")
                print(content)
                raise ValueError("No se pudo extraer JSON")

            json_str = match.group()

            try:
                return json.loads(json_str)
            except Exception:
                print("⚠️ JSON mal formado:")
                print(json_str)
                raise