import sys
import numpy as np
from matplotlib import ticker, pyplot as plt

# width of vacuum opening
ROOMBA_WIDTH = 180

if len(sys.argv) > 1:
    npzfile = np.load(sys.argv[1])

    points = npzfile["points"][:] * 11.8  # convert to mm
    values = npzfile["values"][:]

    minx=np.amin(points, axis=0)[0]
    maxx=np.amax(points, axis=0)[0]

    miny=np.amin(points, axis=0)[1]
    maxy=np.amax(points, axis=0)[1]

    fig, ax = plt.subplots()
    #ax.set_title(u"Floor map", fontsize=20)

    # size and fixed aspect ratio
    fig.set_size_inches(10, 8)
    ax.set_aspect('equal')

    ax.set_xlim(minx-150, maxx+150)
    ax.set_ylim(miny-150, maxy+150)

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

    fig.tight_layout()

    # plot robot path with respect to width of vacuum unit (e.g. 180mm)
    # from https://stackoverflow.com/questions/19394505/matplotlib-expand-the-line-with-specified-width-in-data-unit#42972469 
    # if you want to updated lines (e.g. resize plot) take the full code from that answer
    lw = ((ax.transData.transform((1, ROOMBA_WIDTH))-ax.transData.transform((0, 0)))*(72./fig.dpi))[1]
    plt.plot(points[:,0], points[:,1], '-', color="steelblue", linewidth=lw, alpha=.9)

    # plot path (and position samples)
    plt.plot(points[:,0], points[:,1], '-', color="white", markersize=2, linewidth=.75, alpha=.5)

    # plot start and end position 
    start_pos = plt.Circle((points[0,0], points[0,1]), 50, color='white', linewidth=2, alpha=.5, zorder=100)
    ax.add_artist(start_pos)

    final_pos = plt.Circle((points[-1,0], points[-1,1]), 50, color='lime', linewidth=2, alpha=.5, zorder=101)
    ax.add_artist(final_pos)

    plt.savefig(sys.argv[1]+".png", format="png", dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')     # save as file (800x600)
    plt.show()
