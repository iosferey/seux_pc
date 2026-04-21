#Promt actualizado: Evaluación heurística personalizada
LLM_PROMPT_TEMPLATE = """
Actúa como evaluador experto en experiencia de usuario (UX).

Evalúa el sitio web proporcionado con base en 5 categorías heurísticas.
Utiliza una escala Likert de 1 a 5 donde:

1 = Muy deficiente
2 = Deficiente
3 = Aceptable
4 = Bueno
5 = Excelente

Categorías:

A_control_jerarquia:
Evalúa la claridad de la estructura, jerarquía visual, control del usuario y organización del contenido.

B_lenguaje_modelos:
Evalúa la correspondencia entre el lenguaje del sistema, los símbolos y los modelos mentales del usuario.

C_cognicion_memoria:
Evalúa la carga cognitiva, facilidad de comprensión y necesidad de memorización.

D_eficiencia_tiempo:
Evalúa la rapidez de interacción, optimización de tareas y fluidez del uso.

E_error_riesgo:
Evalúa la prevención de errores, recuperación y claridad comunicativa.

INSTRUCCIONES ESTRICTAS:

- NO incluyas explicaciones
- NO uses markdown
- NO agregues texto adicional
- SOLO devuelve JSON válido
- Todos los valores deben ser enteros entre 1 y 5

Formato obligatorio:

{{
  "A_control_jerarquia": 1,
  "B_lenguaje_modelos": 1,
  "C_cognicion_memoria": 1,
  "D_eficiencia_tiempo": 1,
  "E_error_riesgo": 1
}}

HTML:
{html}
"""

#Promt 1: Evaluación heurística
# heuristic_prompt = """
# Evalúa el sitio web descrito según las 10 heurísticas de Nielsen.

# Devuelve SOLO un JSON con este formato:

# {
# "H1":1-5,
# "H2":1-5,
# "H3":1-5,
# "H4":1-5,
# "H5":1-5,
# "H6":1-5,
# "H7":1-5,
# "H8":1-5,
# "H9":1-5,
# "H10":1-5
# }

# Escala:
# 1 = muy deficiente
# 5 = excelente
# """

# country_prompt = """
# Analiza el siguiente contenido web.

# Determina el país principal al que parece dirigirse el sitio.

# Responde SOLO con el nombre del país.
# """