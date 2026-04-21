def analyze_typography(soup):

    fonts = set()

    # Buscar fuentes en estilos inline
    for tag in soup.find_all(style=True):
        style = tag.get("style", "").lower()

        if "font-family" in style:
            try:
                value = style.split("font-family:")[1].split(";")[0]
                fonts.add(value.strip())
            except:
                pass

    # Detectar jerarquía de encabezados
    headings = {
        "h1": len(soup.find_all("h1")),
        "h2": len(soup.find_all("h2")),
        "h3": len(soup.find_all("h3")),
        "h4": len(soup.find_all("h4")),
        "h5": len(soup.find_all("h5")),
        "h6": len(soup.find_all("h6")),
    }

    total_headings = sum(headings.values())

    return {
        "font_families": list(fonts),
        "font_count": len(fonts),
        "heading_structure": headings,
        "total_headings": total_headings
    }