import numpy as np
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

npzfile = np.load("path1.npz")

points = npzfile["points"] * 11.8   # convert to mm
values = npzfile["values"]

minx=np.amin(points, axis=0)[0]
maxx=np.amax(points, axis=0)[0]

miny=np.amin(points, axis=0)[1]
maxy=np.amax(points, axis=0)[1]

grid_x, grid_y = np.mgrid[minx:maxx:100j, miny:maxy:100j]
raw = griddata(points, values, (grid_x, grid_y), method='linear')

#plt.imshow(raw.T, origin='lower', extent=(minx,maxx,miny,maxy))


# plot a line, with 'linewidth' in (y-)data coordinates.       
fig1, ax1 = plt.subplots()
ax1.set_aspect('equal')

data_linewidth_plot(points[:,0], points[:,1], ax=ax1, linewidth=180, alpha=0.8)

# plot path and position samples
#plt.plot(points[:,0], points[:,1], 'ko-', markersize=2, linewidth=1.0, alpha=.5)

""" plot arrows colored by time """
plt.set_cmap("gist_rainbow")
plt.quiver(points[:,0][:-1], points[:,1][:-1], points[:,0][1:]-points[:,0][:-1], points[:,1][1:]-points[:,1][:-1], range(len(points)), scale_units='xy', angles='xy', scale=1, zorder=99)

""" plot arrows colored by heading """
#plt.set_cmap("hsv")
#plt.quiver(points[:,0][:-1], points[:,1][:-1], points[:,0][1:]-points[:,0][:-1], points[:,1][1:]-points[:,1][:-1], values, scale_units='xy', angles='xy', scale=1, zorder=99)

start_pos = plt.Circle((points[0,0], points[0,1]), 350/4, color='grey', alpha=.75, zorder=100)
ax1.add_artist(start_pos)

final_pos = plt.Circle((points[-1,0], points[-1,1]), 350/4, color='green', alpha=.75, zorder=101)
ax1.add_artist(final_pos)

ax1.grid(which="both", zorder=5)
#ax1.set_xticks(np.arange(-2000, 2001, 1000))

plt.show()                        
#plt.savefig("out.png", dpi=150)     # save as file (800x600)