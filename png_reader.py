#!/usr/bin/env python3

import sys
import zlib
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import base64
import cv2

PNG_HEAD = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a" # Magic PNG header bytes
PNG_IEND = b"\x49\x45\x4E\x44"
PNG_ZTXT = b"\x7A\x54\x58\x74" # info is stored in zTXT section


"""
    It might be good to peruse the PNG spec:
    https://www.w3.org/TR/PNG-Structure.html
"""

"""
    This file takes a single argument: path to a PNG file you expect
    contains an embedded draw.io diagram data. This only happens if 'Include a copy of my diagram' was checked when exporting
    This will Read the PNG file, and print the resulting diagram data to stdout.
"""

def inflate(b,b64=False):
    """~2016 draw.io started compressing 'using standard deflate'
        https://about.draw.io/extracting-the-xml-from-mxfiles/
        experience has shown this is deflate WITH NO HEADER
    """
    if b64: # optional, additionally base64 decode
        b = base64.b64decode(b)
    return unquote(zlib.decompress(b,-15).decode('utf8'))

def valid_png(f):
    head = f.read(8)
    if head != PNG_HEAD:
        print("invalid PNG")
        sys.exit(1)

def read_section(f):
    """Sections/chunks are
        4-byte LENGTH
        4-byte SECTION
        <LENGTH> CONTENTS
        4-byte CRC
    """
    length = int.from_bytes(f.read(4), byteorder='big',signed=False) # in bytes
    sectype = f.read(4)

    contents = f.read(length)
    f.read(4) # skip CRC int
    # or f.seek(4, 1) to just move 4 bytes forward from current

    return sectype,contents

def image_reader(filename):

    image = cv2.imread(filename)
    cv2.imshow("frame", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return "Success"

def main():
    ztxt = {}
    with open(sys.argv[1], "rb") as f:
        valid_png(f)
        while f.read(1) != b'':
            f.seek(-1,1)
            sectype,contents = read_section(f)
            if sectype == PNG_IEND:
                break
            elif sectype == PNG_ZTXT:
                idx=0
                while contents[idx] != 0:
                    idx += 1
                keyname = contents[:idx].decode('ascii')
                data = contents[idx+2:] # skip two NUL bytes
                ztxt[keyname] = data

    """
        Basically, the PNG should have a zTXT section, which is
        itself like a key/value store. It should have a key of
        mxGraphModel. The data for that key is compressed XML,
        which has node with text in it. That text is base64 encoded,
        and again compressed. So undoing all of that we get XML again,
        of the true mxGraphModel. That graph model is what draw.io
        uses to recompute the diagram. You can even paste it in 
        Extras > Edit Diagram.
    """

    xml = inflate(ztxt['mxGraphModel'])
    mxfile = ET.fromstring(xml)[0].text
    diagram = inflate(mxfile,b64=True)

if __name__ == "__main__":
    image_reader(sys.argv[1])