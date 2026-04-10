import re
import sys
from pathlib import Path


BODY_RE = re.compile(r"body\s*\{(?P<body>.*?)\}", re.IGNORECASE | re.DOTALL)
PAGE_RE = re.compile(r"\.(page|container)\s*\{(?P<block>.*?)\}", re.IGNORECASE | re.DOTALL)
VIEWPORT_RE = re.compile(r'<meta[^>]+name=["\']viewport["\'][^>]+content=["\'][^"\']*width=1080', re.IGNORECASE)
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*(\d+)px", re.IGNORECASE)
GAP_RE = re.compile(r"gap\s*:\s*(\d+)px", re.IGNORECASE)
GRID_REPEAT_RE = re.compile(r"grid-template-columns\s*:\s*repeat\(\s*([0-9]+)", re.IGNORECASE)
CARD_LIKE_RE = re.compile(r"\.(hero|card|panel|section)\s*\{(?P<block>.*?)\}", re.IGNORECASE | re.DOTALL)


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def block_has(block: str, pattern: str) -> bool:
    return re.search(pattern, block, re.IGNORECASE) is not None


def main() -> int:
    if len(sys.argv) != 2:
        return fail("usage: python scripts/validate_html.py <card.html>")

    path = Path(sys.argv[1])
    if not path.exists():
        return fail(f"file not found: {path}")

    html = path.read_text(encoding="utf-8")
    lowered = html.lower()
    if "<html" not in lowered or "</html>" not in lowered:
        return fail("not a complete HTML document")

    if not VIEWPORT_RE.search(html):
        return fail('missing viewport meta with content containing "width=1080"')

    body_match = BODY_RE.search(html)
    if not body_match:
        return fail("missing body CSS block")
    body_block = body_match.group("body")

    if not block_has(body_block, r"width\s*:\s*1080px"):
        return fail("body must set width: 1080px")
    if not block_has(body_block, r"min-height\s*:\s*100vh"):
        return fail("body must set min-height: 100vh")
    if block_has(body_block, r"(?<!-)height\s*:"):
        return fail("body must not set a fixed height")

    page_match = PAGE_RE.search(html)
    if not page_match:
        return fail("missing .page or .container CSS block")
    page_block = page_match.group("block")

    if not (
        block_has(page_block, r"margin\s*:\s*0\s+auto")
        or block_has(body_block, r"padding\s*:\s*\d+px")
    ):
        return fail("main container must be centered")

    for match in GRID_REPEAT_RE.finditer(html):
        if int(match.group(1)) >= 3:
            return fail("detected 3+ column desktop-style layout")

    font_sizes = [int(match.group(1)) for match in FONT_SIZE_RE.finditer(html)]
    if font_sizes:
        if max(font_sizes) < 48:
            return fail("missing a clearly prominent title size (>= 48px)")
        if min(font_sizes) < 22:
            return fail("detected font-size below 22px, which is too small for mobile share cards")

    gaps = [int(match.group(1)) for match in GAP_RE.finditer(html)]
    if gaps and max(gaps) < 20:
        return fail("layout gap is too tight; mobile share cards need at least 20px spacing")

    card_paddings: list[int] = []
    for match in CARD_LIKE_RE.finditer(html):
        block = match.group("block")
        padding_match = re.search(r"padding\s*:\s*(\d+)px", block, re.IGNORECASE)
        if padding_match:
            card_paddings.append(int(padding_match.group(1)))
    if card_paddings and max(card_paddings) < 28:
        return fail("card-like sections need at least 28px padding for mobile readability")

    print("OK: card.html passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
