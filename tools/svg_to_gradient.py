"""Load a gradient from an SVG file and print it as a python datastructure."""

import re
import sys
import pprint
from xml.etree.ElementTree import parse

STOP_REGEX = re.compile(
    r'\bstop-color\s*:\s*'
    r'#(?P<r>[0-9a-f]{2})'
    r'(?P<g>[0-9a-f]{2})'
    r'(?P<b>[0-9a-f]{2})',
    re.I
)

def load_gradient(filename):
    with open(filename) as f:
        doc = parse(f)
    gradient = []
    for stop in doc.findall('.//{http://www.w3.org/2000/svg}stop'):
        frac = float(stop.get('offset'))
        mo = STOP_REGEX.search(
            stop.get('style')
        )
        colour = (
            int(mo.group('r'), 16) / 255.0,
            int(mo.group('g'), 16) / 255.0,
            int(mo.group('b'), 16) / 255.0,
        )
        gradient.append((frac, colour))
    return gradient


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        pprint.pprint(
            load_gradient(filename),
            indent=4,
            width=80
        )
