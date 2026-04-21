from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from .color import analyze_colors
from .typography import analyze_typography
from .layout import analyze_layout
from .components import analyze_components


class VisualAnalyzer:

    def __init__(self, url):
        self.url = url

    def load(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )
            page = browser.new_page(viewport={"width": 1366, "height": 768})

            page.goto(self.url, wait_until="networkidle")

            html = page.content()
            screenshot = page.screenshot(full_page=True)

            browser.close()

        return html, screenshot

    def run_analysis(self):
        html, screenshot = self.load()
        soup = BeautifulSoup(html, "html.parser")

        return {
            "typography": analyze_typography(soup),
            "color": analyze_colors(screenshot),
            "layout": analyze_layout(soup),
            "components": analyze_components(soup)
        }