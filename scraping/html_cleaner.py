from bs4 import BeautifulSoup
from config.settings import MAX_TEXT_LENGTH

def clean_html(html):

    soup = BeautifulSoup(html,"html.parser")

    for tag in soup(["script","style","noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    return text[:MAX_TEXT_LENGTH]