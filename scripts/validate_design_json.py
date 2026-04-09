import json
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL = {"meta", "colors", "fonts", "layout", "effects"}
REQUIRED_META = {"version", "style_id", "style_name", "source", "reason"}
REQUIRED_COLORS = {
    "page_background",
    "surface",
    "primary",
    "accent",
    "text_primary",
    "text_secondary",
}
REQUIRED_FONTS = {"title_family", "body_family", "title_size", "body_size"}
REQUIRED_LAYOUT = {
    "canvas_width",
    "min_height",
    "page_padding",
    "container_width",
    "section_gap",
    "card_padding",
    "card_radius",
}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def ensure_text_size(value: str, minimum: int, name: str) -> None:
    if not isinstance(value, str) or not value.endswith("px"):
        raise ValueError(f"{name} must be a px string")
    try:
        size = int(value[:-2])
    except ValueError as exc:
        raise ValueError(f"{name} must be a px string") from exc
    if size < minimum:
        raise ValueError(f"{name} must be at least {minimum}px")


def main() -> int:
    if len(sys.argv) != 2:
        return fail("usage: python scripts/validate_design_json.py <design.json>")

    path = Path(sys.argv[1])
    if not path.exists():
        return fail(f"file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")

    missing_top = REQUIRED_TOP_LEVEL - data.keys()
    if missing_top:
        return fail(f"missing top-level keys: {', '.join(sorted(missing_top))}")

    for group_name, required in (
        ("meta", REQUIRED_META),
        ("colors", REQUIRED_COLORS),
        ("fonts", REQUIRED_FONTS),
        ("layout", REQUIRED_LAYOUT),
    ):
        group = data.get(group_name)
        if not isinstance(group, dict):
            return fail(f"{group_name} must be an object")
        missing = required - group.keys()
        if missing:
            return fail(f"missing {group_name} keys: {', '.join(sorted(missing))}")

    meta = data["meta"]
    if meta["source"] not in {"preset", "generated"}:
        return fail("meta.source must be preset or generated")

    layout = data["layout"]
    if layout["canvas_width"] != "1080px":
        return fail("layout.canvas_width must be 1080px")
    if layout["min_height"] != "100vh":
        return fail("layout.min_height must be 100vh")

    try:
        ensure_text_size(data["fonts"]["title_size"], 48, "fonts.title_size")
        ensure_text_size(data["fonts"]["body_size"], 28, "fonts.body_size")
    except ValueError as exc:
        return fail(str(exc))

    blob = json.dumps(data, ensure_ascii=False).lower()
    if "<html" in blob or "<style" in blob:
        return fail("design.json must not contain HTML or CSS content")

    print("OK: design.json passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
