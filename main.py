#!/usr/bin/env python3
"""ai-excited-01 entry: copy the bundled excitement image to /output/entry.png.

The entry image is a joyful robot bursting with excitement -- arms thrown
high, huge sparkling eyes, fireworks and confetti all around, and a big
yellow "WOW!" starburst behind it. This program does nothing creative at
run time: it validates the bundled PNG, copies it byte-for-byte to the
output directory, and proves the copy is identical before it exits.

Pure standard library only. No clock, no randomness, no network, no
model calls -- both runs therefore produce exactly the same bytes.
"""

import hashlib
import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576          # 1 MiB
MAX_WIDTH = 1024
MAX_HEIGHT = 1024


def read_png_dimensions(path):
    """Return (width, height) parsed from the PNG IHDR chunk."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != PNG_MAGIC:
        raise ValueError("not a PNG file: bad magic bytes")
    chunk_length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or chunk_length != 13:
        raise ValueError("not a PNG file: first chunk is not IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "entry.png")
    output_dir = "/output"
    output_path = os.path.join(output_dir, "entry.png")

    if not os.path.isfile(source_path):
        print("error: entry.png not found beside main.py", file=sys.stderr)
        return 1

    width, height = read_png_dimensions(source_path)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        print(
            "error: image is %dx%d, over the %dx%d limit"
            % (width, height, MAX_WIDTH, MAX_HEIGHT),
            file=sys.stderr,
        )
        return 1

    with open(source_path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        print(
            "error: image is %d bytes, above the %d byte cap"
            % (len(data), MAX_BYTES),
            file=sys.stderr,
        )
        return 1

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "wb") as handle:
        handle.write(data)

    with open(output_path, "rb") as handle:
        written = handle.read()
    if written != data:
        print("error: written bytes do not match the source", file=sys.stderr)
        return 1

    digest = hashlib.sha256(data).hexdigest()
    print("output: %s" % output_path)
    print("dimensions: %dx%d" % (width, height))
    print("bytes: %d" % len(data))
    print("sha256: %s" % digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
