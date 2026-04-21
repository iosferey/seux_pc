def analyze_components(soup):

    navbars = soup.find_all("nav")
    footers = soup.find_all("footer")
    buttons = soup.find_all("button")
    forms = soup.find_all("form")

    # Detección heurística de componentes tipo "card"
    cards = soup.find_all(
        class_=lambda x: x and any(
            keyword in x.lower() for keyword in ["card", "item", "box"]
        )
    )

    return {
        "navbar_count": len(navbars),
        "footer_count": len(footers),
        "button_count": len(buttons),
        "form_count": len(forms),
        "card_count": len(cards)
    }