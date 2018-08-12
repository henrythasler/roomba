import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

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



npzfile = np.load("2018-08-05_191829_path.npz")

points = npzfile["points"] * 11.8  # convert to mm
values = npzfile["values"]

# plot a line, with 'linewidth' in (y-)data coordinates.       
fig, ax = plt.subplots()
#ax.set_title(u"Floor map", fontsize=20)

#plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

# fixed aspect ratio
ax.set_aspect('equal')

# set background colors
fig.patch.set_facecolor('#065da2')
ax.set_facecolor('#065da2')

#ax.xaxis.set_ticklabels([])
#ax.yaxis.set_ticklabels([])
#ax.axis('off')

ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')


# plot robot path with respect to width of vacuum unit (180mm)
data_linewidth_plot(points[:,0], points[:,1], ax=ax, linewidth=180, alpha=.75, color="steelblue")

# plot path and position samples
#plt.plot(points[:,0], points[:,1], 'ko-', markersize=2, linewidth=1.0, alpha=.5)

""" plot arrows colored by time """
plt.set_cmap("gist_rainbow")
#qw = ((ax.transData.transform((1, 50))-ax.transData.transform((0, 0)))*(72./fig.dpi))[1]
plt.quiver(points[:,0][:-1], points[:,1][:-1], points[:,0][1:]-points[:,0][:-1], points[:,1][1:]-points[:,1][:-1], range(len(points)), scale_units='xy', angles='xy', width=.002, scale=1, zorder=99)

""" plot arrows colored by heading """
#plt.set_cmap("hsv")
#plt.quiver(points[:,0][:-1], points[:,1][:-1], points[:,0][1:]-points[:,0][:-1], points[:,1][1:]-points[:,1][:-1], values, scale_units='xy', angles='xy', scale=1, zorder=99)

start_pos = plt.Circle((points[0,0], points[0,1]), 50, color='red', alpha=.5, zorder=100)
ax.add_artist(start_pos)

final_pos = plt.Circle((points[-1,0], points[-1,1]), 50, color='magenta', alpha=.5, zorder=101)
ax.add_artist(final_pos)

ax.grid(which="both", zorder=5)
ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1000))
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1000))

ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(500))
ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(500))

#fig.tight_layout()
plt.show()                        
#plt.savefig("out.png", dpi=150)     # save as file (800x600)