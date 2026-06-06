from seuxpc.config.hofstede import comparable_dimensions

class CulturalTransfer:

    def compute(self, source, target):

        diff = 0
        dimensions = comparable_dimensions(source, target)

        if not dimensions:
            return 0

        for d in dimensions:
            diff += abs(source[d] - target[d])

        # normalización: cada dimensión Hofstede normalizada tiene rango aproximado 0-1.
        max_diff = len(dimensions)

        similarity = 1 - (diff / max_diff)

        return similarity
