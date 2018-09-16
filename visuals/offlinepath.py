import sys
import numpy as np
from matplotlib import ticker, pyplot as plt

# width of vacuum opening
ROOMBA_WIDTH = 180
SCALING_FACTOR = 10

class data_linewidth_plot():
    """ from https://stackoverflow.com/questions/19394505/matplotlib-expand-the-line-with-specified-width-in-data-unit#42972469 """
    def __init__(self, x, y, **kwargs):
        self.ax = kwargs.pop("ax", plt.gca())
        self.fig = self.ax.get_figure()
        self.lw_data = kwargs.pop("linewidth", 1)
        self.lw = 1
        self.fig.canvas.draw()
        self.timer = None

        self.ppd = 72./self.fig.dpi
        self.trans = self.ax.transData.transform
        self.linehandle, = self.ax.plot([],[],**kwargs)
        if "label" in kwargs: kwargs.pop("label")
        self.line, = self.ax.plot(x, y, **kwargs)
        self.line.set_color(self.linehandle.get_color())
        self._resize()
        self.cid = self.fig.canvas.mpl_connect('draw_event', self._resize)

    def _resize(self, event=None):
        lw =  ((self.trans((1, self.lw_data))-self.trans((0, 0)))*self.ppd)[1]
        if lw != self.lw:
            self.line.set_linewidth(lw)
            self.lw = lw
            self._redraw_later()

    def _callback(self):
        #print(self.lw)
        self.fig.canvas.draw_idle()

    def _redraw_later(self):
        """ this is some strange workaround for updating the figure """
        if not self.timer:
            self.timer = self.fig.canvas.new_timer(interval=2000)
            self.timer.single_shot = False
            self.timer.add_callback(self._callback)
            self.timer.start()


if len(sys.argv) > 1:
    npzfile = np.load(sys.argv[1])

    points = npzfile["points"][:] * 11.8  # convert to mm
    values = npzfile["values"][:]

    minx=np.amin(points, axis=0)[0]
    maxx=np.amax(points, axis=0)[0]

    miny=np.amin(points, axis=0)[1]
    maxy=np.amax(points, axis=0)[1]

    fig = plt.figure(figsize=(10,8), dpi=100)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)    

    #ax.set_title(u"Floor map", fontsize=20)

    # size and fixed aspect ratio
    ax.set_aspect('equal')

    ax.set_xlim(minx-ROOMBA_WIDTH, maxx+ROOMBA_WIDTH)
    ax.set_ylim(miny-ROOMBA_WIDTH, maxy+ROOMBA_WIDTH)

    # set background colors
    fig.patch.set_facecolor('#065da2')
    ax.set_facecolor('#065da2')

    # setup grid
    ax.grid(which="both", linestyle="dotted", linewidth=1, alpha=.5, zorder=5)

    # spacing 0.5m
    ax.xaxis.set_major_locator(ticker.MultipleLocator(500))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(500))

    # all off
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)

    # call this before any transformations. reason is unknown
    fig.canvas.draw()   


    # plot robot path with respect to width of vacuum unit (e.g. 180mm)
    # from https://stackoverflow.com/questions/19394505/matplotlib-expand-the-line-with-specified-width-in-data-unit#42972469 
    # if you want to updated lines (e.g. resize plot) take the full code from that answer 

    # simple
    #lw = ((ax.transData.transform((0, ROOMBA_WIDTH))-ax.transData.transform((0, 0)))*(72./fig.dpi))[1]
    #plt.plot(points[:,0], points[:,1], '-', color="steelblue", linewidth=lw, alpha=.9, solid_capstyle="butt")

    # full
    data_linewidth_plot(points[:,0], points[:,1], ax=ax, color="steelblue", linewidth=ROOMBA_WIDTH, alpha=.9, solid_capstyle="butt")


    # plot path (and position samples)
    plt.plot(points[:,0], points[:,1], '-', color="white", markersize=2, linewidth=.75, alpha=.5)

    # plot start and end position 
    start_pos = plt.Circle((points[0,0], points[0,1]), 100, color='white', linewidth=2, alpha=.5, zorder=100)
    ax.add_artist(start_pos)

    final_pos = plt.Circle((points[-1,0], points[-1,1]), 100, color='lime', linewidth=2, alpha=.5, zorder=101)
    ax.add_artist(final_pos)

    plt.savefig(sys.argv[1]+".png", format="png", dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')     # save as file (800x600)
    plt.show()
