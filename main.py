"""Deliver the ai-excited-01 entry image.

Reads entry.png sitting next to this script, checks that it is a real
PNG within the bounty limits, and writes an exact copy to
/output/entry.png. Pure standard library; nothing here touches the
clock, randomness, the network, or any model.
"""

import hashlib
import os
import struct
import sys

SOURCE_NAME = "entry.png"
DEST_DIR = "/output"
DEST_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def read_png_size(blob):
    # A PNG always starts with its 8-byte signature, then the IHDR
    # chunk; the width and height are the first two big-endian
    # 32-bit fields inside that chunk.
    if blob[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG signature")
    if len(blob) < 24 or blob[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk where one is expected")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    dest_dir = DEST_DIR
    dest = os.path.join(dest_dir, DEST_NAME)

    try:
        with open(source, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        fail("cannot read %s: %s" % (source, exc))

    if len(blob) > MAX_BYTES:
        fail("entry.png is %d bytes, over the %d byte limit "
             "(shrink it before running again)"
             % (len(blob), MAX_BYTES))

    width, height = read_png_size(blob)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail("entry.png is %dx%d, over the %dx%d limit"
             % (width, height, MAX_WIDTH, MAX_HEIGHT))

    try:
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest, "wb") as handle:
            handle.write(blob)
        with open(dest, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        fail("cannot write %s: %s" % (dest, exc))

    if written != blob:
        fail("written file does not match entry.png byte for byte")

    digest = hashlib.sha256(blob).hexdigest()
    print("path: " + dest)
    print("dimensions: %dx%d" % (width, height))
    print("bytes: %d" % len(blob))
    print("sha256: " + digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
