class VisualScorer:

    def __init__(self, data):
        self.d = data

    def compute(self):

        t = self.score_typography()
        c = self.score_color()
        l = self.score_layout()
        u = self.score_components()

        return (t + c + l + u) / 4

    # ------------------

    def score_typography(self):
        fonts = self.d["typography"]["font_count"]
        headings = self.d["typography"]["total_headings"]

        # menos fuentes = mejor
        font_score = 1 / (1 + fonts)

        # más jerarquía = mejor (hasta cierto punto)
        hierarchy_score = min(headings / 10, 1)

        return (font_score + hierarchy_score) / 2

    # ------------------

    def score_color(self):
        colors = self.d["color"]["color_count"]

        if 3 <= colors <= 5:
            return 1
        elif colors < 3:
            return 0.6
        else:
            return max(0.3, 1 - (colors - 5) * 0.1)

    # ------------------

    def score_layout(self):
        whitespace = self.d["layout"]["whitespace_ratio"]
        return min(1, whitespace)

    # ------------------

    def score_components(self):
        comp = self.d["components"]

        score = 0

        if comp["navbar_count"] > 0:
            score += 1

        if comp["footer_count"] > 0:
            score += 1

        score += min(comp["button_count"] / 10, 1)
        score += min(comp["card_count"] / 10, 1)

        return score / 4