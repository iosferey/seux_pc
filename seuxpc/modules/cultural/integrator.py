from seuxpc.config.constants import HEURISTIC_CATEGORIES, CULTURAL_DIMENSIONS
from seuxpc.config.hofstede import get_dimension_value
from seuxpc.config.sensitivity_matrix import SENSITIVITY_MATRIX

class CulturalIntegrator:

    def __init__(self, cultural_vector):
        self.Cj = cultural_vector

    def adjust(self, H):
        adjusted = {}

        for h in HEURISTIC_CATEGORIES:

            influence = sum(
                SENSITIVITY_MATRIX.loc[h, c] * get_dimension_value(self.Cj, c)
                for c in CULTURAL_DIMENSIONS
            )

            adjusted[h] = H[h] * (1 + influence)

        return adjusted

    def adjust_normalized(self, H):
        adjusted = {}

        for h in HEURISTIC_CATEGORIES:
            influence = sum(
                SENSITIVITY_MATRIX.loc[h, c] * get_dimension_value(self.Cj, c)
                for c in CULTURAL_DIMENSIONS
            )

            max_influence = sum(
                SENSITIVITY_MATRIX.loc[h, c]
                for c in CULTURAL_DIMENSIONS
            )

            raw_score = float(H[h])
            h_norm = (raw_score - 1.0) / 4.0
            h_norm = max(0.0, min(1.0, h_norm))

            scaling = (1.0 + influence) / (1.0 + max_influence)
            adjusted[h] = h_norm * scaling

        return adjusted
