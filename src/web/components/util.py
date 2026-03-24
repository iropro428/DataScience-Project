"""Small utility helpers used across the web app."""


def hex_rgba(hex_color: str, alpha: float = 0.2) -> str:
    """Convert a hex color in #rrggbb format to an rgba(...) string for Plotly."""
    hex_value = hex_color.lstrip("#")
    red = int(hex_value[0:2], 16)
    green = int(hex_value[2:4], 16)
    blue = int(hex_value[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha})"
