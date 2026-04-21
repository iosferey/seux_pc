import os
from seuxpc.modules.pipeline.engine import SEUXPC
from seuxpc.utils.io import save_result_json

url = "https://stripe.com"

model = SEUXPC(
    url=url,
    target_country="MX",
    api_key=os.getenv("OPENAI_API_KEY")
)

result = model.run()

path = save_result_json(result, url)
print("Guardado en:", path)