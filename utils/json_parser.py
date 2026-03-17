import json

def parse_json(text):

    try:
        return json.loads(text)
    except:
        return {}