"""Put the Slider package root on sys.path.

The Slider modules (`parser`, `renderer`, `theme`) are imported by bare name
rather than as a package, so the tests need the directory that contains them on
the import path.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
