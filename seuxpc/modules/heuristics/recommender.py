import json
import re

from openai import OpenAI

from seuxpc.config.prompts import LLM_RECOMMENDER_PROMPT_TEMPLATE
from seuxpc.config.settings import (
    RECOMMENDER_MODEL,
    RECOMMENDER_TEMPERATURE,
    MAX_RECOMMENDER_INPUT_CHARS,
    SCORE_BANDS,
)


class HeuristicRecommender:

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate(self, result):
        if not isinstance(result, dict):
            raise ValueError("El resultado de entrada debe ser un dict")

        if self.client:
            try:
                llm_result = self._generate_with_llm(result)
                llm_result["source"] = "llm"
                return llm_result
            except Exception as e:
                print("[WARN] Error generando recomendaciones IA:", e)
                print("[WARN] Usando recomendaciones estaticas")

        static_result = self._generate_static(result)
        static_result["source"] = "static"
        return static_result

    def _generate_with_llm(self, result):
        payload = self._build_payload(result)
        payload_str = json.dumps(payload, ensure_ascii=False)
        payload_trimmed = payload_str[:MAX_RECOMMENDER_INPUT_CHARS]

        prompt = (
            LLM_RECOMMENDER_PROMPT_TEMPLATE
            .replace("{score_bands}", json.dumps(SCORE_BANDS, ensure_ascii=False))
            .replace("{payload}", payload_trimmed)
        )

        response = self.client.chat.completions.create(
            model=RECOMMENDER_MODEL,
            temperature=RECOMMENDER_TEMPERATURE,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Eres un consultor UX senior que entrega recomendaciones accionables.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Respuesta vacia del recomendador")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)

            if not match:
                raise ValueError("No se pudo extraer JSON en recomendaciones")

            parsed = json.loads(match.group())

        self._validate_structure(parsed)
        return parsed

    def _build_payload(self, result):
        heuristics = result.get("heuristics", {})
        visual = result.get("visual_analysis", {})

        ich = result.get("ICH_norm", result.get("ICH"))
        iac = result.get("IAC_norm", result.get("IAC"))
        gap = result.get("Brecha_norm_signed", result.get("Brecha"))

        return {
            "scores": {
                "ICH": ich,
                "IAC": iac,
                "IVS": result.get("IVS"),
                "Brecha": gap,
            },
            "pais_origen": result.get("pais_origen"),
            "pais_objetivo": result.get("pais_objetivo"),
            "transferencia_cultural": result.get("transferencia_cultural", {}),
            "heuristics": heuristics,
            "visual_analysis": {
                "typography": visual.get("typography", {}),
                "color": visual.get("color", {}),
                "layout": visual.get("layout", {}),
                "components": visual.get("components", {}),
            },
        }

    def _validate_structure(self, parsed):
        required_keys = [
            "nivel_global",
            "resumen",
            "acciones_priorizadas",
            "quick_wins",
        ]

        for key in required_keys:
            if key not in parsed:
                raise ValueError(f"Falta clave requerida en recomendaciones: {key}")

        if not isinstance(parsed["acciones_priorizadas"], list):
            raise ValueError("acciones_priorizadas debe ser una lista")

        if not isinstance(parsed["quick_wins"], list):
            raise ValueError("quick_wins debe ser una lista")

    def _generate_static(self, result):
        ich = self._safe_float(result.get("ICH_norm", result.get("ICH")))
        iac = self._safe_float(result.get("IAC_norm", result.get("IAC")))
        ivs = self._safe_float(result.get("IVS"))
        gap = self._safe_float(result.get("Brecha_norm_signed", result.get("Brecha")))

        heuristics = result.get("heuristics", {})
        visual = result.get("visual_analysis", {})

        acciones = []

        if ich < SCORE_BANDS["critico"]:
            acciones.append(
                self._action(
                    1,
                    "heuristica",
                    "Calidad heuristica global critica",
                    "Rediseniar los flujos criticos con checklist heuristico y validacion por tareas top.",
                    "alto",
                )
            )

        if iac < SCORE_BANDS["bajo"]:
            acciones.append(
                self._action(
                    len(acciones) + 1,
                    "cultural",
                    "Baja alineacion cultural con el pais objetivo",
                    "Adaptar tono, ejemplos, convenciones visuales y microcopys al contexto del pais objetivo.",
                    "alto",
                )
            )

        if ivs < SCORE_BANDS["medio"]:
            acciones.append(
                self._action(
                    len(acciones) + 1,
                    "visual",
                    "Indice visual bajo",
                    "Reducir complejidad visual y reforzar jerarquia, contraste y consistencia de componentes.",
                    "medio",
                )
            )

        if gap < -0.05:
            acciones.append(
                self._action(
                    len(acciones) + 1,
                    "cultural",
                    "Brecha cultural negativa",
                    "Priorizar ajustes en contenidos, iconografia y flujos para disminuir friccion cultural.",
                    "alto",
                )
            )

        acciones.extend(self._heuristic_actions(heuristics, start=len(acciones) + 1))
        acciones.extend(self._visual_actions(visual, start=len(acciones) + 1))

        acciones = acciones[:5]

        nivel = self._global_level(ich, iac, ivs)
        resumen = self._summary_for_level(nivel)

        quick_wins = [
            "Normalizar tipografias a 2 familias maximas y escala de encabezados consistente.",
            "Reducir paleta a 3-5 colores funcionales y mejorar contraste texto-fondo.",
            "Reescribir copys clave con lenguaje local del pais objetivo.",
        ]

        return {
            "nivel_global": nivel,
            "resumen": resumen,
            "acciones_priorizadas": acciones,
            "quick_wins": quick_wins,
        }

    def _heuristic_actions(self, heuristics, start):
        low_actions = []

        catalog = {
            "A_control_jerarquia": "Reordenar bloques segun prioridad de tarea y visibilidad de acciones primarias.",
            "B_lenguaje_modelos": "Alinear etiquetas e iconos con lenguaje del usuario y evitar tecnicismos.",
            "C_cognicion_memoria": "Reducir carga cognitiva con pasos guiados, chunks y estado visible.",
            "D_eficiencia_tiempo": "Optimizar recorridos de alta frecuencia y minimizar pasos redundantes.",
            "E_error_riesgo": "Incluir validacion preventiva y mensajes de error accionables.",
        }

        for key, recommendation in catalog.items():
            score = self._safe_float(heuristics.get(key), default=3)

            if score <= 2.5:
                low_actions.append(
                    self._action(
                        start + len(low_actions),
                        "heuristica",
                        f"Bajo desempeno en {key}",
                        recommendation,
                        "alto",
                    )
                )

        return low_actions

    def _visual_actions(self, visual, start):
        actions = []

        typography = visual.get("typography", {})
        color = visual.get("color", {})
        layout = visual.get("layout", {})
        components = visual.get("components", {})

        if self._safe_float(typography.get("font_count"), default=2) > 3:
            actions.append(
                self._action(
                    start + len(actions),
                    "visual",
                    "Exceso de familias tipograficas",
                    "Limitar a 2 familias tipograficas para mejorar legibilidad y coherencia.",
                    "medio",
                )
            )

        if self._safe_float(color.get("color_count"), default=4) > 5:
            actions.append(
                self._action(
                    start + len(actions),
                    "visual",
                    "Paleta de color dispersa",
                    "Consolidar paleta primaria/secundaria y definir reglas de uso por componente.",
                    "medio",
                )
            )

        if self._safe_float(layout.get("whitespace_ratio"), default=0.3) < 0.22:
            actions.append(
                self._action(
                    start + len(actions),
                    "visual",
                    "Bajo espacio en blanco",
                    "Aumentar espaciado vertical y horizontal para separar tareas y mejorar escaneo.",
                    "medio",
                )
            )

        if self._safe_float(components.get("navbar_count"), default=1) == 0:
            actions.append(
                self._action(
                    start + len(actions),
                    "visual",
                    "Navegacion principal ausente",
                    "Agregar navbar persistente con arquitectura de informacion clara.",
                    "alto",
                )
            )

        return actions

    def _global_level(self, ich, iac, ivs):
        base = min(ich, iac, ivs)

        if base < SCORE_BANDS["critico"]:
            return "critico"
        if base < SCORE_BANDS["bajo"]:
            return "bajo"
        if base < SCORE_BANDS["medio"]:
            return "medio"
        return "alto"

    def _summary_for_level(self, level):
        summaries = {
            "critico": "La experiencia actual presenta fricciones severas y requiere intervencion prioritaria.",
            "bajo": "La experiencia es funcional pero con brechas relevantes que afectan desempeno y percepcion.",
            "medio": "La experiencia es aceptable con oportunidades claras de optimizacion.",
            "alto": "La experiencia es solida; conviene optimizar detalles para maximizar consistencia y conversion.",
        }
        return summaries[level]

    def _action(self, prioridad, area, hallazgo, recomendacion, impacto):
        return {
            "prioridad": prioridad,
            "area": area,
            "hallazgo": hallazgo,
            "recomendacion": recomendacion,
            "impacto_estimado": impacto,
        }

    def _safe_float(self, value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
