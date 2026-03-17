def interpret_scores(ICH, IAC_origin, IAC_mexico):

    interpretation = {}

    # Interpretación de calidad heurística
    if ICH >= 4.5:
        interpretation["quality"] = "Excelente usabilidad"
    elif ICH >= 4.0:
        interpretation["quality"] = "Muy buena usabilidad"
    elif ICH >= 3.0:
        interpretation["quality"] = "Usabilidad adecuada"
    elif ICH >= 2.0:
        interpretation["quality"] = "Usabilidad deficiente"
    else:
        interpretation["quality"] = "Problemas críticos de usabilidad"

    # Brecha cultural
    gap = IAC_origin - IAC_mexico

    if gap < 0.2:
        transfer = "Alta transferibilidad cultural"
    elif gap < 0.5:
        transfer = "Transferible con ajustes menores"
    elif gap < 1:
        transfer = "Requiere adaptación cultural moderada"
    else:
        transfer = "Requiere rediseño cultural significativo"

    interpretation["transferability"] = transfer
    interpretation["gap"] = round(gap, 2)

    return interpretation