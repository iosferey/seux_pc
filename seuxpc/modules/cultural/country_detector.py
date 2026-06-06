import json
import re
import unicodedata
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from openai import OpenAI

from seuxpc.config.hofstede import HOFSTEDE, get_country_profile, normalize_country_code
from seuxpc.config.settings import OPENAI_MODEL, TEMPERATURE, MAX_HTML_CHARS


TLD_COUNTRY_HINTS = {
    "ar": "ARG",
    "au": "AUL",
    "br": "BRA",
    "ca": "CAN",
    "ch": "SWI",
    "cl": "CHL",
    "cn": "CHI",
    "co": "COL",
    "de": "GER",
    "dk": "DEN",
    "es": "SPA",
    "fi": "FIN",
    "fr": "FRA",
    "gb": "GBR",
    "gr": "GRE",
    "hk": "HOK",
    "ie": "IRE",
    "in": "IND",
    "it": "ITA",
    "jp": "JPN",
    "kr": "KOR",
    "mx": "MEX",
    "nl": "NET",
    "nz": "NZL",
    "pe": "PER",
    "pt": "POR",
    "ru": "RUS",
    "se": "SWE",
    "sg": "SIN",
    "th": "THA",
    "tr": "TUR",
    "uk": "GBR",
    "us": "USA",
    "uy": "URU",
    "ve": "VEN",
    "vn": "VIE",
    "za": "SAF",
}


class CountryDetector:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key) if api_key else None

    def detect(self, html, url=None, fallback="USA"):
        code = self._detect_from_url(url)

        if code:
            return code

        code = self._detect_from_html(html)

        if code:
            return code

        code = self._detect_with_llm(html, url)

        if code:
            return code

        return normalize_country_code(fallback) or "USA"

    def _detect_from_url(self, url):
        if not url:
            return None

        host = urlparse(url).netloc.lower()
        parts = [part for part in host.split(".") if part]

        for part in reversed(parts):
            hinted_code = TLD_COUNTRY_HINTS.get(part)

            if hinted_code and get_country_profile(hinted_code):
                return hinted_code

        return None

    def _detect_from_html(self, html):
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        for attr in ("lang", "content"):
            for value in self._meta_values(soup, attr):
                code = self._code_from_text(value)

                if code:
                    return code

        text = soup.get_text(" ", strip=True)
        return self._code_from_text(text[:MAX_HTML_CHARS])

    def _detect_with_llm(self, html, url):
        if not self.client or not html:
            return None

        html_trimmed = html.strip().replace("\n", " ")[:MAX_HTML_CHARS]
        valid_codes = ", ".join(sorted(HOFSTEDE.keys()))

        prompt = f"""
Infer the primary country audience for this website.
Return JSON only with this shape: {{"country_code": "MEX", "country": "Mexico"}}.
Use one of these Hofstede country codes: {valid_codes}.
URL: {url or ""}
HTML excerpt: {html_trimmed}
""".strip()

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=TEMPERATURE,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You infer a website's target country from content, locale, currency, URLs and language.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)
        except Exception as e:
            print("[WARN] Error detectando pais con OpenAI:", e)
            return None

        return normalize_country_code(parsed.get("country_code") or parsed.get("country"))

    def _meta_values(self, soup, attr):
        values = []

        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            values.append(html_tag.get("lang"))

        for tag in soup.find_all("meta"):
            value = tag.get(attr)

            if value:
                values.append(value)

        return values

    def _code_from_text(self, text):
        if not text:
            return None

        text_lower = text.lower()

        locale_match = re.search(r"\b([a-z]{2})[-_]([a-z]{2})\b", text_lower)
        if locale_match:
            code = normalize_country_code(locale_match.group(2))

            if code:
                return code

        text_key = self._compact_text(text_lower)

        for code, profile in HOFSTEDE.items():
            country = profile.get("country")

            if country and re.search(rf"\b{re.escape(country.lower())}\b", text_lower):
                return code

            country_key = self._compact_text(country)

            if country_key and len(country_key) > 3 and country_key in text_key:
                return code

        return None

    def _compact_text(self, value):
        if not value:
            return ""

        text = unicodedata.normalize("NFKD", str(value).lower())
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return re.sub(r"[^a-z0-9]+", "", text)
