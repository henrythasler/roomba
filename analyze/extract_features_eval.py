import os
import sys

import matplotlib.pyplot as plt

import numpy as np

from skimage import io
from skimage.morphology import convex_hull_image, watershed
from skimage import img_as_float
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage.feature import corner_harris, corner_subpix, corner_peaks, peak_local_max
from skimage import measure

from scipy import ndimage as ndi

if len(sys.argv) > 1:
    source = io.imread(sys.argv[1])
    source = rgb2gray(source)

    fig, axes = plt.subplots(3, 3, figsize=(7, 6), sharex=True, sharey=True)
    ax = axes.ravel()    
    for a in ax.ravel():
        a.axis('off')

    ax[0].imshow(source, interpolation='nearest')
    ax[0].set_title("Original image")

    chull = convex_hull_image(source)
    ax[1].imshow(img_as_float(chull), interpolation='nearest')
    ax[1].set_title("convex_hull_image")

    s = np.linspace(0, 2*np.pi, 400)
    x = 400 + 260*np.cos(s)
    y = 300 + 360*np.sin(s)
    init = np.array([x, y]).T

    snake = active_contour(gaussian(source, 2),
                        init, alpha=0.015, beta=10, gamma=0.001)

    ax[2].imshow(source)
    ax[2].plot(init[:, 0], init[:, 1], '--r', lw=3)
    ax[2].plot(snake[:, 0], snake[:, 1], '-b', lw=3)
    ax[2].set_title("active_contour")

    coords = corner_peaks(corner_harris(source), min_distance=5)
    coords_subpix = corner_subpix(source, coords, window_size=13)

    ax[3].imshow(source)
    ax[3].plot(coords[:, 1], coords[:, 0], '.r', markersize=6)
    ax[3].plot(coords_subpix[:, 1], coords_subpix[:, 0], '+r', markersize=15)
    ax[3].set_title("Corner detection")

    # Find contours at a constant value of 0.8
    contours = measure.find_contours(source, 0.5)
    ax[4].imshow(source)
    for n, contour in enumerate(contours):
        contour = measure.approximate_polygon(contour, tolerance=10)
        ax[4].plot(contour[:, 1], contour[:, 0], linewidth=4)
    ax[4].set_title("find_contours")


    distance = ndi.distance_transform_edt(source)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((3, 3)),
                                labels=source)
    markers = ndi.label(local_maxi)[0]
    labels = watershed(-distance, markers, mask=source)

    #ax[5].imshow(source, cmap=plt.cm.gray, interpolation='nearest')
    ax[5].imshow(labels, interpolation='nearest')
    ax[5].set_title("watershed")


    ax[6].imshow(img_as_float(chull), interpolation='nearest')
    ax[6].set_title("convex_hull with contour")
    contours = measure.find_contours(chull, 0.5)
    for n, contour in enumerate(contours):
        ax[6].plot(contour[:, 1], contour[:, 0], linewidth=4)

    plt.tight_layout()
    plt.show()