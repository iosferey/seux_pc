import pandas as pd

SENSITIVITY_MATRIX = pd.DataFrame({
    "DP":  [1.00, 0.75, 0.50, 0.50, 0.50, 0.50],
    "IND": [0.75, 0.75, 0.75, 0.75, 0.75, 0.75],
    "EI":  [0.75, 1.00, 1.00, 0.75, 1.00, 1.00],
    "OLP": [0.50, 0.75, 0.75, 0.75, 0.75, 0.75],
    "LCS": [0.50, 0.50, 0.50, 0.75, 0.75, 0.75],
    "OGI": [0.50, 0.75, 0.75, 1.00, 0.75, 1.00]
},
index=[
    "A_control_jerarquia",
    "B_lenguaje_modelos",
    "C_cognicion_memoria",
    "D_eficiencia_tiempo",
    "E_error_riesgo",
    "F_conexion_narrativa_simbolica"
])