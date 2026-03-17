from openai import OpenAI
import os
from dotenv import load_dotenv

from config.settings import MODEL_NAME
from ai.prompts import country_prompt

# Cargar variables .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def detect_country(text):
    """
    Detecta el país objetivo principal del sitio web.
    """

    prompt = country_prompt + "\n\nContenido del sitio:\n" + text

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        country = response.choices[0].message.content.strip()

        return country

    except Exception as e:
        print("⚠️ Error detectando país:", e)
        return "USA"