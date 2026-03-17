from config.sensitivity_matrix import sensitivity
from analysis.metrics import calculate_ich

def calculate_indices(scores, culture):

    weights = {}

    for h in sensitivity.index:

        base = 1

        # SOLO usar dimensiones existentes
        adjustment = sum(
            sensitivity.loc[h][dim] * culture[dim]
            for dim in sensitivity.columns
        )

        weights[h] = base + adjustment

    ICH = calculate_ich(scores)

    weighted_sum = sum(
        scores[h] * weights[h]
        for h in scores
    )

    IAC = weighted_sum / sum(weights.values())

    return ICH, IAC