"""Click-to-add interface with explicit computation, clear and export buttons."""

from .geometry import Point, Box
from .diagram import construct
from .io import write_csv, write_json
from .visualize import draw


class InteractiveController:
    def __init__(self, figure, axes, sites=(), box=None, output='interactive.png'):
        self.figure, self.axes = figure, axes
        self.sites = list(sites)
        self.box = box or Box(0,0,1,1)
        self.output = output
        self.diagram = None
        self.status = figure.text(.13,.02,'Click to add sites; Compute or double-click to build.',fontsize=9)
        self.figure.canvas.mpl_connect('button_press_event',self.click)
        self.clear_axes()

    def clear_axes(self):
        self.axes.clear()
        b = self.box
        self.axes.set(xlim=(b.xmin,b.xmax),ylim=(b.ymin,b.ymax),xlabel='x',ylabel='y',
                      title='Fortune sweep | click to add points')
        self.axes.set_aspect('equal')
        if self.sites:
            self.axes.scatter([p.x for p in self.sites],[p.y for p in self.sites],c='black')

    def click(self,event):
        if event.inaxes is not self.axes or event.button != 1 or event.xdata is None:
            return
        if event.dblclick:
            self.compute()
            return
        self.sites.append(Point(event.xdata,event.ydata))
        self.diagram = None
        self.clear_axes()
        self.status.set_text(f'{len(self.sites)} input sites; compute to update the cells.')
        self.figure.canvas.draw_idle()

    def compute(self,event=None):
        if not self.sites:
            self.status.set_text('Add at least one site first.')
            return
        try:
            self.diagram = construct(self.sites,self.box)
            draw(self.diagram,self.axes)
            stats = self.diagram.statistics
            self.status.set_text(f"{stats['unique_sites']} cells; {stats['construction_seconds']:.4f} s. Export saves image, CSV and JSON.")
        except (ValueError,ArithmeticError) as exc:
            self.status.set_text(str(exc))
        self.figure.canvas.draw_idle()

    def clear(self,event=None):
        self.sites.clear()
        self.diagram = None
        self.clear_axes()
        self.status.set_text('Cleared. Click to add new sites.')
        self.figure.canvas.draw_idle()

    def export(self,event=None):
        from pathlib import Path
        if self.diagram is None:
            self.compute()
        if self.diagram is None:
            return
        path = Path(self.output)
        path.parent.mkdir(parents=True,exist_ok=True)
        self.figure.savefig(path,dpi=160)
        write_csv(self.diagram,path.with_suffix('.csv'))
        write_json(self.diagram,path.with_suffix('.json'))
        self.status.set_text(f'Saved {path.name}, CSV and JSON.')
        self.figure.canvas.draw_idle()


def launch(sites=(),box=None,output='interactive.png'):
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button
    fig, axes = plt.subplots(figsize=(9,8))
    fig.subplots_adjust(bottom=.17)
    controller = InteractiveController(fig,axes,sites,box,output)
    controller.buttons = []
    for x,label,callback in ((.18,'Compute',controller.compute),(.43,'Clear',controller.clear),(.68,'Export',controller.export)):
        button = Button(fig.add_axes([x,.075,.15,.05]),label)
        button.on_clicked(callback)
        controller.buttons.append(button)
    plt.show()
    return controller
