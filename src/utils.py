import pandas as pd
import base64

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