import csv
import json
from types import SimpleNamespace

import pytest

from fortune.cli import main
from fortune.diagram import construct
from fortune.geometry import Point
from fortune.io import random_sites, read_sites, write_csv, write_json


def test_coordinate_parser_and_error(tmp_path):
    path = tmp_path / "sites.txt"
    path.write_text("# comment\n1 2\n3,4 # note\n", encoding="utf-8")
    assert read_sites(path) == [Point(1, 2), Point(3, 4)]
    path.write_text("1 2 3", encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        read_sites(path)


def test_export_preserves_order_duplicates_and_infinite_edges(tmp_path):
    d = construct([(0, 0), (1, 0), (0, 1), (0, 0)])
    write_csv(d, tmp_path / "cells.csv")
    write_json(d, tmp_path / "diagram.json")
    payload = json.loads((tmp_path / "diagram.json").read_text())
    assert payload["cells"][0]["input_indices"] == [0, 3]
    assert any(e["kind"] == "ray" and e["direction"] for e in payload["edges"])
    rows = list(csv.DictReader((tmp_path / "cells.csv").open()))
    first = [r for r in rows if r["cell"] == "0"]
    assert [int(r["vertex_order"]) for r in first] == list(range(len(first)))
    assert (first[-1]["next_x"], first[-1]["next_y"]) == (first[0]["x"], first[0]["y"])


def test_batch_cli_exports_and_seed(tmp_path, capsys):
    assert random_sites(10, 19) == random_sites(10, 19)
    image = tmp_path / "result.png"
    assert (
        main(
            [
                "--random",
                "12",
                "--seed",
                "19",
                "--output",
                str(image),
                "--csv",
                str(tmp_path / "cells.csv"),
            ]
        )
        == 0
    )
    assert image.read_bytes().startswith(b"\x89PNG")
    assert json.loads(capsys.readouterr().out)["cells"] == 12
    assert main(["--random", "0"]) == 2


def test_interactive_callbacks_compute_clear_and_export(tmp_path):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    from fortune.interactive import InteractiveController

    fig = Figure()
    FigureCanvasAgg(fig)
    axes = fig.subplots()
    ui = InteractiveController(fig, axes, output=str(tmp_path / "interactive.png"))
    ui.compute()
    for x, y in ((0.2, 0.2), (0.8, 0.2), (0.5, 0.8)):
        ui.click(
            SimpleNamespace(inaxes=axes, button=1, xdata=x, ydata=y, dblclick=False)
        )
    ui.click(
        SimpleNamespace(inaxes=axes, button=1, xdata=0.5, ydata=0.8, dblclick=True)
    )
    assert ui.diagram is not None and len(ui.diagram.cells) == 3
    ui.export()
    assert (tmp_path / "interactive.csv").exists()
    ui.clear()
    assert not ui.sites and ui.diagram is None
