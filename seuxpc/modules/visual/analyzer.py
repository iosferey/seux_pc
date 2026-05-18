from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

from .color import analyze_colors
from .typography import analyze_typography
from .layout import analyze_layout
from .components import analyze_components
from seuxpc.config.settings import PLAYWRIGHT_NAV_TIMEOUT_MS, PLAYWRIGHT_WAIT_UNTIL


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

            try:
                page.goto(
                    self.url,
                    wait_until=PLAYWRIGHT_WAIT_UNTIL,
                    timeout=PLAYWRIGHT_NAV_TIMEOUT_MS,
                )
            except PlaywrightTimeoutError:
                # Fallback para sitios que mantienen conexiones abiertas y nunca llegan a "networkidle".
                page.goto(self.url, wait_until="load", timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)

            html = page.content()
            screenshot = page.screenshot(full_page=True)

            browser.close()

        return html, screenshot

    def run_analysis(self, html=None, screenshot=None):
        if html is None or screenshot is None:
            html, screenshot = self.load()

        soup = BeautifulSoup(html, "html.parser")

        return {
            "typography": analyze_typography(soup),
            "color": analyze_colors(screenshot),
            "layout": analyze_layout(soup),
            "components": analyze_components(soup)
        }