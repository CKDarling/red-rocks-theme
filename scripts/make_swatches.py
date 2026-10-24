"""Write small RGBA PNG swatches (solid fill, faint 1px border) using only the stdlib."""
import struct, sys, zlib
from pathlib import Path

W, H = 48, 20
BORDER = (0, 0, 0, 70)  # translucent so it reads on light and dark GitHub themes


def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def png(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    rows = b""
    for y in range(H):
        rows += b"\x00"
        for x in range(W):
            edge = x in (0, W - 1) or y in (0, H - 1)
            rows += bytes(BORDER if edge else (r, g, b, 255))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9))
            + chunk(b"IEND", b""))


out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
for h in sys.argv[2:]:
    (out / f"{h}.png").write_bytes(png(h))
    print(out / f"{h}.png")
