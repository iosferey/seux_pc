from seuxpc.config.constants import HEURISTIC_CATEGORIES, CULTURAL_DIMENSIONS

def validate_inputs(heuristics, cultural_vector):

    if set(heuristics.keys()) != set(HEURISTIC_CATEGORIES):
        raise ValueError("Heurísticas inválidas")

    if set(cultural_vector.keys()) != set(CULTURAL_DIMENSIONS):
        raise ValueError("Dimensiones culturales inválidas")