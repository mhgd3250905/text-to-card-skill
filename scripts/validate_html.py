import re
import sys
from pathlib import Path


BODY_RE = re.compile(r"body\s*\{(?P<body>.*?)\}", re.IGNORECASE | re.DOTALL)
PAGE_RE = re.compile(r"\.(page|container)\s*\{(?P<block>.*?)\}", re.IGNORECASE | re.DOTALL)
VIEWPORT_RE = re.compile(r'<meta[^>]+name=["\']viewport["\'][^>]+content=["\'][^"\']*width=1080', re.IGNORECASE)


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

    if "grid-template-columns: repeat(3" in lowered:
        return fail("detected desktop-style multi-column layout")

    print("OK: card.html passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
