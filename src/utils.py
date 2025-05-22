import pandas as pd
import base64
import colorsys

def encode_image_to_base64(path):
    # Could do encorde for all in advance and cache
    with open(path, 'rb') as f:
        image_bytes = f.read()
    encoded = base64.b64encode(image_bytes).decode()
    return f'data:image/png;base64,{encoded}'

def format_time(minutes: float) -> str:
    total_seconds = int(minutes * 60)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    else:
        return f"{m}:{s}"

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple (0–1 scale)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple (0–1 scale) to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
    )

def generate_shades_plotly(hex_color, n_shades=3, ban=False):
    """Generate n_shades of a hex color using HSV value scaling."""
    r, g, b = hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    if n_shades == 5:
        if ban: value_steps = [0.2, 0.4, 0.6, 0.8, 1]
        else: value_steps = [1, 0.85, 0.6, 0.45, .3]
    else:
        if ban: value_steps = [0.3, 0.5, 0.7]
        else: value_steps = [0.9, 0.7, 0.5]
    shades = [colorsys.hsv_to_rgb(h, s, val) for val in value_steps]

    return [rgb_to_hex(rgb) for rgb in shades]