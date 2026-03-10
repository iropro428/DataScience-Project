def hex_rgba(hex_color: str, alpha: float = 0.2) -> str:
    """#rrggbb → rgba(r,g,b,alpha) fuer Plotly fillcolor."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
