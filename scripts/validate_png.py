import argparse
import struct
import sys
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def read_png(path: Path) -> tuple[int, int, int, int, list[bytes]]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != PNG_SIGNATURE:
            raise ValueError("invalid PNG signature")
        width = height = bit_depth = color_type = 0
        compressed = bytearray()

        while True:
            header = handle.read(8)
            if len(header) != 8:
                raise ValueError("unexpected end of file")
            length, chunk_type = struct.unpack(">I4s", header)
            data = handle.read(length)
            handle.read(4)  # CRC

            if chunk_type == b"IHDR":
                if length < 13:
                    raise ValueError("invalid IHDR chunk")
                width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                    ">IIBBBBB", data[:13]
                )
                if compression != 0 or filter_method != 0 or interlace != 0:
                    raise ValueError("unsupported PNG compression/filter/interlace mode")
            elif chunk_type == b"IDAT":
                compressed.extend(data)
            elif chunk_type == b"IEND":
                break

        if not width or not height:
            raise ValueError("missing IHDR chunk")
        if bit_depth != 8 or color_type not in {2, 6}:
            raise ValueError("unsupported PNG color format; expected 8-bit RGB or RGBA")

        pixel_bytes = 3 if color_type == 2 else 4
        stride = width * pixel_bytes
        raw = zlib.decompress(bytes(compressed))
        expected = height * (stride + 1)
        if len(raw) != expected:
            raise ValueError("unexpected decompressed PNG size")

        rows: list[bytes] = []
        previous = bytearray(stride)
        offset = 0
        for _ in range(height):
            filter_type = raw[offset]
            offset += 1
            row = bytearray(raw[offset : offset + stride])
            offset += stride

            if filter_type == 1:
                for index in range(stride):
                    left = row[index - pixel_bytes] if index >= pixel_bytes else 0
                    row[index] = (row[index] + left) & 0xFF
            elif filter_type == 2:
                for index in range(stride):
                    row[index] = (row[index] + previous[index]) & 0xFF
            elif filter_type == 3:
                for index in range(stride):
                    left = row[index - pixel_bytes] if index >= pixel_bytes else 0
                    up = previous[index]
                    row[index] = (row[index] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                for index in range(stride):
                    left = row[index - pixel_bytes] if index >= pixel_bytes else 0
                    up = previous[index]
                    up_left = previous[index - pixel_bytes] if index >= pixel_bytes else 0
                    row[index] = (row[index] + paeth_predictor(left, up, up_left)) & 0xFF
            elif filter_type != 0:
                raise ValueError(f"unsupported PNG filter type: {filter_type}")

            rows.append(bytes(row))
            previous = row

        return width, height, color_type, pixel_bytes, rows


def analyze_rows(rows: list[bytes], width: int, pixel_bytes: int) -> tuple[float, int]:
    sample_stride = max(1, width // 64)
    white_like = 0
    total = 0
    colors: set[tuple[int, int, int, int]] = set()

    for row in rows:
        for x in range(0, width, sample_stride):
            start = x * pixel_bytes
            red = row[start]
            green = row[start + 1]
            blue = row[start + 2]
            alpha = row[start + 3] if pixel_bytes == 4 else 255
            total += 1
            if red >= 245 and green >= 245 and blue >= 245 and alpha >= 245:
                white_like += 1
            if len(colors) < 256:
                colors.add((red, green, blue, alpha))

    white_ratio = white_like / total if total else 0.0
    return white_ratio, len(colors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--expected-width", type=int, default=None)
    parser.add_argument("--min-height", type=int, default=None)
    parser.add_argument("--min-ratio", type=float, default=None)
    parser.add_argument("--reject-blank", action="store_true")
    parser.add_argument("--max-white-ratio", type=float, default=0.98)
    parser.add_argument("--min-unique-colors", type=int, default=8)
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        return fail(f"file not found: {path}")

    try:
        width, height, _color_type, pixel_bytes, rows = read_png(path)
    except ValueError as exc:
        return fail(str(exc))

    if args.expected_width is not None and width != args.expected_width:
        return fail(f"width must be {args.expected_width}px, got {width}px")
    if args.min_height is not None and height < args.min_height:
        return fail(f"height must be at least {args.min_height}px, got {height}px")
    if args.min_ratio is not None and width > 0:
        ratio = height / width
        if ratio < args.min_ratio:
            return fail(f"height/width ratio must be at least {args.min_ratio}, got {ratio:.2f}")

    if args.reject_blank:
        white_ratio, unique_colors = analyze_rows(rows, width, pixel_bytes)
        if white_ratio >= args.max_white_ratio:
            return fail(f"image is mostly white ({white_ratio:.2%})")
        if unique_colors < args.min_unique_colors:
            return fail(f"image appears too uniform ({unique_colors} sampled colors)")

    print(f"OK: card.png passed validation ({width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
