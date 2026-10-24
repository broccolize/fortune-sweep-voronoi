# Engineering Decisions

## D001 Personal project with an assignment quality benchmark

The owner clarified that this is a personal project. The supplied specification
defines the technical and documentation standard. Git milestone dates follow the
owner's requested schedule; actual tests and measurements are independently
recorded. No unfinished feature receives a completion commit.

## D002 Native Windows execution and WSL assistance

Keep this Windows workspace for native delivery and GUI verification. Pi 0.86.0
is available in Debian WSL. Keep separate environments for Windows and Linux;
never share virtual environment binaries.

Microsoft recommends matching filesystem and tool OS for performance:
https://learn.microsoft.com/en-us/windows/wsl/filesystems

Matplotlib supports Windows and Linux:
https://matplotlib.org/stable/install/

## D003 Balanced AVL beach line

Use an AVL tree of arcs in geometric order with predecessor/successor links.
Rotations preserve the order; local insertion and removal maintain adjacency.
The tree provides a worst-case logarithmic height bound.

## D004 Independent validation

Query ownership must be checked in the constructed polygons before comparison
with a brute-force nearest-site scan. No Voronoi/Delaunay library or all-pairs
cell-construction substitute may be used in the production algorithm.
