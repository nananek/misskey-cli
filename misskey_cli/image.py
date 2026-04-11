"""Terminal image rendering using xterm 256-color ANSI half blocks.

Two pixels per character cell (upper half = fg, lower half = bg of '\u2580'),
so the output row count is ``ceil(image_height / 2)`` characters.
"""
import io

import requests


HALF_BLOCK = "\u2580"  # U+2580 UPPER HALF BLOCK
RESET = "\x1b[0m"


def rgb_to_256(r, g, b):
    """Map an 8-bit RGB triple to the nearest xterm 256-color index."""
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return 232 + round((r - 8) / 247 * 24)
    return (
        16
        + 36 * round(r / 255 * 5)
        + 6 * round(g / 255 * 5)
        + round(b / 255 * 5)
    )


def _resize_for_terminal(image, max_width):
    """Resize ``image`` so its width is at most ``max_width``, preserving aspect.

    Height is not halved here — ``render_image_256`` iterates two source rows per
    output line, so the final visual aspect matches the source on a terminal
    with roughly 2:1 cell height.
    """
    from PIL import Image  # lazy import

    w, h = image.size
    if w <= max_width:
        return image
    ratio = max_width / w
    new_w = max_width
    new_h = max(1, int(round(h * ratio)))
    return image.resize((new_w, new_h), Image.LANCZOS)


def render_image_256(image_bytes, max_width=76):
    """Render raw image bytes as ANSI 256-color half-block text.

    Returns a terminal-ready string; the caller writes it to stdout.
    """
    from PIL import Image  # lazy import

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = _resize_for_terminal(img, max_width)
    pixels = img.load()
    w, h = img.size

    lines = []
    for y in range(0, h, 2):
        buf = []
        last_fg = None
        last_bg = None
        for x in range(w):
            top = pixels[x, y]
            bottom = pixels[x, y + 1] if y + 1 < h else (0, 0, 0)
            fg = rgb_to_256(*top)
            bg = rgb_to_256(*bottom)
            if fg != last_fg:
                buf.append(f"\x1b[38;5;{fg}m")
                last_fg = fg
            if bg != last_bg:
                buf.append(f"\x1b[48;5;{bg}m")
                last_bg = bg
            buf.append(HALF_BLOCK)
        buf.append(RESET)
        buf.append("\n")
        lines.append("".join(buf))
    return "".join(lines)


def render_image_256_from_url(url, max_width=76):
    """Fetch ``url`` and render it via :func:`render_image_256`."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return render_image_256(resp.content, max_width=max_width)
