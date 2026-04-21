def analyze_layout(soup):

    elements = soup.find_all()
    total_elements = len(elements)

    text = soup.get_text().strip()
    text_length = len(text)

    # Densidad visual aproximada
    density = total_elements / (text_length + 1)

    # Espacio en blanco estimado
    whitespace_ratio = 1 / (1 + density)

    return {
        "total_elements": total_elements,
        "text_length": text_length,
        "visual_density": density,
        "whitespace_ratio": whitespace_ratio
    }