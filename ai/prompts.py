heuristic_prompt = """
Evalúa el sitio web descrito según las 10 heurísticas de Nielsen.

Devuelve SOLO un JSON con este formato:

{
"H1":1-5,
"H2":1-5,
"H3":1-5,
"H4":1-5,
"H5":1-5,
"H6":1-5,
"H7":1-5,
"H8":1-5,
"H9":1-5,
"H10":1-5
}

Escala:
1 = muy deficiente
5 = excelente
"""

country_prompt = """
Analiza el siguiente contenido web.

Determina el país principal al que parece dirigirse el sitio.

Responde SOLO con el nombre del país.
"""