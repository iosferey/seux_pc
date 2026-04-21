import re

class CountryDetector:

    def detect(self, html):

        html_lower = html.lower()

        # Reglas simples (puedes escalar después)
        if ".mx" in html_lower or "mexico" in html_lower:
            return "MX"

        if ".es" in html_lower or "españa" in html_lower:
            return "ES"

        if ".uk" in html_lower or "united kingdom" in html_lower:
            return "UK"

        if ".jp" in html_lower or "japan" in html_lower:
            return "JP"

        # fallback
        return "US"