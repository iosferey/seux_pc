from seuxpc.config.constants import HEURISTIC_CATEGORIES

class HeuristicEvaluator:

    def __init__(self, scores):
        self.scores = scores

    def ux_base(self):
        return sum(self.scores[c] for c in HEURISTIC_CATEGORIES) / len(HEURISTIC_CATEGORIES)