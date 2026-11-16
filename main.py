"""Deliver the ai-excited-01 entry image.

Finds entry.png next to this script, checks that it is a real PNG
within the competition limits, and copies it byte-for-byte to
/output/entry.png, verifying the copy matches the original.

Pure standard library. No clock, no randomness, no network.
"""

import hashlib
import os
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
SOURCE_NAME = "entry.png"
DEST_DIR = "/output"


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def read_png_header(path):
    """Return (width, height) after checking magic bytes and IHDR."""
    with open(path, "rb") as handle:
        head = handle.read(33)
    if len(head) < 33 or head[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file: bad magic bytes")
    chunk_len, chunk_type = struct.unpack(">I4s", head[8:16])
    if chunk_type != b"IHDR" or chunk_len != 13:
        raise ValueError("not a PNG file: first chunk is not IHDR")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source):
        return fail("entry.png not found beside main.py")

    try:
        width, height = read_png_header(source)
    except (OSError, ValueError) as exc:
        return fail(str(exc))

    if width > MAX_SIDE or height > MAX_SIDE:
        return fail("image is %dx%d, over the %dx%d limit"
                    % (width, height, MAX_SIDE, MAX_SIDE))

    with open(source, "rb") as handle:
        payload = handle.read()
    if len(payload) != os.path.getsize(source):
        return fail("short read: file changed while reading")
    if len(payload) > MAX_BYTES:
        return fail("image is %d bytes, over the 1 MiB limit"
                    % len(payload))

    os.makedirs(DEST_DIR, exist_ok=True)
    dest = os.path.join(DEST_DIR, SOURCE_NAME)
    with open(dest, "wb") as handle:
        handle.write(payload)
    with open(dest, "rb") as handle:
        written = handle.read()
    if written != payload:
        return fail("verification failed: /output/entry.png differs")

    digest = hashlib.sha256(payload).hexdigest()
    print("source: " + source)
    print("path: " + dest)
    print("dimensions: %dx%d" % (width, height))
    print("bytes: %d" % len(payload))
    print("sha256: " + digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
