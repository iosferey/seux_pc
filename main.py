from dotenv import load_dotenv
import os

load_dotenv()

from scraping.scraper import scrape_site
from scraping.html_cleaner import clean_html

from ai.heuristic_evaluator import evaluate_heuristics
from ai.country_detector import detect_country

from config.cultural_profiles import cultural_profiles

from analysis.cultural_indices import calculate_indices
from analysis.transfer_analysis import transfer_gap
from analysis.interpretation import interpret_scores

from reports.report_generator import generate_report

import sys


def main(url):

    print("Scraping site...")
    html = scrape_site(url)

    clean_text = clean_html(html)

    print("Evaluating heuristics with AI...")
    heuristic_scores = evaluate_heuristics(clean_text)

    print("Detecting target country...")
    country = detect_country(clean_text)

    origin_profile = cultural_profiles.get(country, cultural_profiles["USA"])
    mexico_profile = cultural_profiles["Mexico"]

    # Cálculo de índices
    ICH, IAC_origin = calculate_indices(heuristic_scores, origin_profile)
    _, IAC_mexico = calculate_indices(heuristic_scores, mexico_profile)

    gap = transfer_gap(IAC_origin, IAC_mexico)

    # ✅ Calcular interpretación ANTES del reporte
    interpretation = interpret_scores(ICH, IAC_origin, IAC_mexico)

    # ✅ Pasar interpretación al reporte
    generate_report(
        url,
        country,
        heuristic_scores,
        ICH,
        IAC_origin,
        IAC_mexico,
        gap,
        interpretation
    )


if __name__ == "__main__":
    url = sys.argv[1]
    main(url)