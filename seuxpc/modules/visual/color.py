from colorthief import ColorThief
from PIL import Image
import io
import os


def analyze_colors(screenshot):

    # Guardar temporalmente la imagen
    temp_path = "temp_screenshot.png"

    image = Image.open(io.BytesIO(screenshot))
    image.save(temp_path)

    try:
        ct = ColorThief(temp_path)

        palette = ct.get_palette(color_count=6)

        hex_palette = [
            '#%02x%02x%02x' % color for color in palette
        ]

    except:
        hex_palette = []

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return {
        "palette": hex_palette,
        "color_count": len(hex_palette)
    }