from seuxpc.config.constants import CULTURAL_DIMENSIONS

class CulturalTransfer:

    def compute(self, source, target):

        diff = 0

        for d in CULTURAL_DIMENSIONS:
            diff += abs(source[d] - target[d])

        # normalización (máximo posible = 6 dimensiones)
        max_diff = len(CULTURAL_DIMENSIONS)

        similarity = 1 - (diff / max_diff)

        return similarity