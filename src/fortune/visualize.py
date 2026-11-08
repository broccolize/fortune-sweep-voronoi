"""Matplotlib static rendering; the geometric core has no plotting dependency."""

from .io import ensure_parent


def draw(diagram, axes, *, labels=True):
    from matplotlib import colormaps
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Rectangle

    axes.clear()
    polygons = [[(p.x, p.y) for p in c.vertices] for c in diagram.cells if c.vertices]
    cmap = colormaps["tab20"]
    axes.add_collection(
        PolyCollection(
            polygons,
            facecolors=[cmap(i % 20) for i in range(len(polygons))],
            edgecolors="#3f4754",
            linewidths=0.6,
            alpha=0.65,
        )
    )
    axes.scatter(
        [p.x for p in diagram.sites],
        [p.y for p in diagram.sites],
        s=18,
        c="#101828",
        zorder=3,
    )
    if labels:
        for c in diagram.cells:
            p = diagram.sites[c.site]
            label = "/".join(map(str, c.input_indices))
            axes.annotate(
                label, (p.x, p.y), xytext=(4, 4), textcoords="offset points", fontsize=8
            )
    b = diagram.box
    axes.add_patch(
        Rectangle(
            (b.xmin, b.ymin),
            b.xmax - b.xmin,
            b.ymax - b.ymin,
            fill=False,
            ls="--",
            lw=1.5,
            color="#b42318",
            zorder=4,
        )
    )
    axes.set(
        xlim=(b.xmin, b.xmax),
        ylim=(b.ymin, b.ymax),
        xlabel="x",
        ylabel="y",
        title=f"Fortune sweep | {len(diagram.sites)} sites | {len(diagram.edges)} clipped edges",
    )
    axes.set_aspect("equal", adjustable="box")


def render(diagram, path=None, *, show=False, labels=True):
    if show:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(figsize=(8, 7))
    else:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure

        fig = Figure(figsize=(8, 7))
        FigureCanvasAgg(fig)
        axes = fig.subplots()
    draw(diagram, axes, labels=labels)
    fig.tight_layout()
    if path:
        fig.savefig(ensure_parent(path), dpi=160)
    if show:
        plt.show()
    return fig
