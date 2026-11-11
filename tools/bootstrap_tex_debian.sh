#!/usr/bin/env bash
# Add missing LuaLaTeX font support locally, without sudo or system changes.
set -eu
report_script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
report_project_dir="$(CDPATH= cd -- "$report_script_dir/.." && pwd)"
report_tex_deps="$report_project_dir/tmp/tex-deps"
mkdir -p "$report_tex_deps/packages" "$report_tex_deps/tree"
cd "$report_tex_deps/packages"
set -- "$report_tex_deps"/packages/texlive-luatex_*.deb
if [ ! -f "$1" ]; then
  apt-get download texlive-luatex
fi
for report_tex_package in "$report_tex_deps"/packages/texlive-luatex_*.deb; do
  dpkg-deb --extract "$report_tex_package" "$report_tex_deps/tree"
done
report_cache_base="$(printenv XDG_CACHE_HOME || true)"
if [ -z "$report_cache_base" ]; then
  report_cache_base="$HOME/.cache"
fi
report_cache_dir="$report_cache_base/fortune-sweep-latex"
mkdir -p "$report_cache_dir/texmf" "$report_cache_dir/fonts"
cp -a "$report_tex_deps/tree/usr/share/texlive/texmf-dist/." "$report_cache_dir/texmf/"
mktexlsr "$report_cache_dir/texmf"
python3 - "$report_tex_deps/wsl-paths.json" "$report_cache_dir" <<'PY'
import json
from pathlib import Path
import sys
cache = Path(sys.argv[2])
Path(sys.argv[1]).write_text(json.dumps({
    "texmf_home": str(cache / "texmf"),
    "font_cache": str(cache / "fonts"),
}, indent=2) + "\n", encoding="utf-8")
PY
printf '%s\n' "Local LuaLaTeX support prepared in the Debian user cache; no system packages changed."
