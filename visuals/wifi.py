import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

npzfile = np.load("/home/henry/dev/roomba/logger/2018-08-05_123107_wifi.npz")

points = npzfile["points"] * 11.8   # convert to mm
values = npzfile["values"]

minx=np.amin(points, axis=0)[0]
maxx=np.amax(points, axis=0)[0]

miny=np.amin(points, axis=0)[1]
maxy=np.amax(points, axis=0)[1]

fig, ax = plt.subplots()
#ax.set_title(u"Floor map", fontsize=20)

# fixed aspect ratio
ax.set_aspect('equal')

# set background colors
fig.patch.set_facecolor('#300030')
ax.set_facecolor('#300030')

ax.grid(which="both", zorder=5)
ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))
ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(500))

ax.spines['bottom'].set_color('#300030')
ax.spines['top'].set_color('#300030') 
ax.spines['right'].set_color('#300030')
ax.spines['left'].set_color('#300030')

#ax.xaxis.label.set_color('grey')
ax.tick_params(axis='x', colors='grey')
ax.tick_params(axis='y', colors='grey')

plt.set_cmap("inferno")

grid_x, grid_y = np.mgrid[minx:maxx:100j, miny:maxy:100j]
raw = griddata(points, values, (grid_x, grid_y), method='linear')

#im = plt.imshow(raw, interpolation='lanczos', vmax=abs(raw).max(), vmin=-abs(raw).max())
plt.imshow(raw.T, origin='lower', extent=(minx,maxx,miny,maxy), alpha=.8, zorder=10)
plt.plot(points[:,0], points[:,1], 'k.', ms=5, zorder=11)

#plt.colorbar()
plt.show()