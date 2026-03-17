from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def scrape_site(url):

    options = Options()
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(5)

    html = driver.page_source
    driver.save_screenshot("data/screenshot.png")

    driver.quit()

    return html