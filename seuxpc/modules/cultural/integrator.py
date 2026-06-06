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
