import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

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

    points = npzfile["points"] * 11.8  # convert to mm
    values = npzfile["values"]

    minx=np.amin(points, axis=0)[0]
    maxx=np.amax(points, axis=0)[0]

    miny=np.amin(points, axis=0)[1]
    maxy=np.amax(points, axis=0)[1]

    #plt.imshow(raw.T, origin='lower', extent=(minx,maxx,miny,maxy))


    # plot a line, with 'linewidth' in (y-)data coordinates.       
    fig, ax = plt.subplots()
    #ax.set_title(u"Floor map", fontsize=20)

    #plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    # fixed aspect ratio
    ax.set_aspect('equal')
    fig.set_size_inches(8, 6)

    # set background colors
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    # setup grid
    #ax.grid(which="both", linestyle="dotted", linewidth=1, alpha=.5, zorder=5)
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))

    #ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(500))
    #ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(500))


    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])

    #ax.axis('off')

    #ax.tick_params(axis='x', colors='white')
    #ax.tick_params(axis='y', colors='white')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)

    # plot robot path with respect to width of vacuum unit (180mm)
    data_linewidth_plot(points[:,0], points[:,1], ax=ax, linewidth=200, alpha=1, color="white", solid_capstyle="round")

    fig.tight_layout()
    plt.savefig(sys.argv[1]+".png", format="png", dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')     # save as file (800x600)
    plt.show()                        
