from seuxpc.modules.visual.analyzer import VisualAnalyzer
from seuxpc.modules.heuristics.llm_evaluator import LLMHeuristicEvaluator
from seuxpc.modules.heuristics.evaluator import HeuristicEvaluator
from seuxpc.modules.cultural.integrator import CulturalIntegrator
from seuxpc.modules.cultural.country_detector import CountryDetector
from seuxpc.modules.cultural.transfer import CulturalTransfer
from seuxpc.modules.scoring.visual_scorer import VisualScorer
from seuxpc.modules.scoring.seux_scorer import SEUXScorer

from seuxpc.config.hofstede import HOFSTEDE


class SEUXPC:

    def __init__(self, url, target_country, api_key):
        self.url = url
        self.target_country = target_country
        self.api_key = api_key

    def run(self):

        # ---------------------------
        # 1. CARGA Y ANÁLISIS VISUAL
        # ---------------------------
        analyzer = VisualAnalyzer(self.url)
        html, _ = analyzer.load()

        visual_data = analyzer.run_analysis()

        # ---------------------------
        # 2. DETECCIÓN DE PAÍS ORIGEN
        # ---------------------------
        source_country = CountryDetector().detect(html)

        if source_country not in HOFSTEDE:
            source_country = "US"

        source_culture = HOFSTEDE[source_country]

        if self.target_country not in HOFSTEDE:
            raise ValueError(f"País objetivo no soportado: {self.target_country}")

        target_culture = HOFSTEDE[self.target_country]

        # ---------------------------
        # 3. EVALUACIÓN HEURÍSTICA (LLM)
        # ---------------------------
        try:
            heuristics = LLMHeuristicEvaluator(self.api_key).evaluate(html)

        except Exception as e:
            print("⚠️ Error en LLM:", e)
            print("⚠️ Usando fallback heurístico")

            heuristics = {
                "A_control_jerarquia": 3,
                "B_lenguaje_modelos": 3,
                "C_cognicion_memoria": 3,
                "D_eficiencia_tiempo": 3,
                "E_error_riesgo": 3
            }

        # ---------------------------
        # 4. UX BASE (ICH base)
        # ---------------------------
        ux = HeuristicEvaluator(heuristics).ux_base()

        # ---------------------------
        # 5. AJUSTE CULTURAL (IAC)
        # ---------------------------
        adjusted = CulturalIntegrator(target_culture).adjust(heuristics)
        ux_c = sum(adjusted.values()) / len(adjusted)

        # ---------------------------
        # 6. TRANSFERENCIA CULTURAL
        # ---------------------------
        transfer = CulturalTransfer().compute(source_culture, target_culture)

        # ---------------------------
        # 7. ÍNDICE VISUAL (IVS)
        # ---------------------------
        ivs = VisualScorer(visual_data).compute()

        # ---------------------------
        # 8. SCORING FINAL
        # ---------------------------
        result = SEUXScorer().compute(ux, ux_c, ivs)

        # ---------------------------
        # 9. METADATOS
        # ---------------------------
        result["transferencia_cultural"] = transfer
        result["pais_origen"] = source_country
        result["pais_objetivo"] = self.target_country
        result["visual_analysis"] = visual_data
        result["heuristics"] = heuristics

        return result