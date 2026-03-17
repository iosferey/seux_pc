from analysis import interpretation


def generate_report(url, country, scores, ICH, IAC_origin, IAC_mexico, gap, interpretation):

    print("\n--- UX Cultural Evaluation ---")

    print("Site:",url)
    print("Detected Country:",country)

    print("\nHeuristic Scores:",scores)

    print("\nICH:",round(ICH,2))
    print("IAC Origin:",round(IAC_origin,2))
    print("IAC Mexico:",round(IAC_mexico,2))

    print("Transfer Gap:",round(gap,2))

    print("\nInterpretación:")

    print("Calidad heurística:", interpretation["quality"])
    print("Transferibilidad cultural:", interpretation["transferability"])
    print("Brecha cultural:", interpretation["gap"])