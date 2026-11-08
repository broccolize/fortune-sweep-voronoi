"""An independently implemented Fortune sweep; no Voronoi libraries are used."""

__version__ = "0.1.0"

from .diagram import construct
from .geometry import Box, Point

__all__ = ["construct", "Point", "Box", "__version__"]
