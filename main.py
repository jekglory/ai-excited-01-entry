"""Copy the ai-excited-01 entry image to the grader output directory.

Reads entry.png from beside this file, checks it really is a PNG of the
right size, and writes an exact byte-for-byte copy to /output/entry.png.
Only the Python standard library is used; the run is fully deterministic.
"""

import hashlib
import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024


def fail(message):
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def read_png_header(path):
    """Return (width, height) after checking the PNG signature and IHDR."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if len(head) < 33 or head[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG magic bytes")
    if head[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk where one is expected")
    ihdr_length = struct.unpack(">I", head[8:12])[0]
    if ihdr_length != 13:
        fail("entry.png has a malformed IHDR chunk")
    width, height = struct.unpack(">II", head[16:24])
    bit_depth, colour_type = head[24], head[25]
    if bit_depth not in (1, 2, 4, 8, 16):
        fail("entry.png has an unsupported bit depth: %d" % bit_depth)
    if colour_type not in (0, 2, 3, 4, 6):
        fail("entry.png has an unsupported colour type: %d" % colour_type)
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        fail("entry.png not found beside main.py")

    width, height = read_png_header(source)
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        fail("entry.png is %dx%d, over the %dx%d limit"
             % (width, height, MAX_WIDTH, MAX_HEIGHT))

    with open(source, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % len(data))

    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)

    with open(target, "rb") as handle:
        written = handle.read()
    if written != data:
        fail("written copy does not match entry.png")

    digest = hashlib.sha256(data).hexdigest()
    print("wrote: " + target)
    print("dimensions: %dx%d" % (width, height))
    print("bytes: %d" % len(data))
    print("sha256: " + digest)


if __name__ == "__main__":
    main()
