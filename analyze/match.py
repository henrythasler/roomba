import sys
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np


fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(9.3, 6), sharex=True, sharey=True)
fig.subplots_adjust(left=0.03, right=0.97, hspace=0.3, wspace=0.05)
ax = axes.ravel()    
for a in ax.ravel():
    a.axis('off')
    a.set_aspect('equal')

# load test data
if len(sys.argv) > 2:
    
    img1 = cv.imread(sys.argv[1], cv.IMREAD_GRAYSCALE)
    img2 = cv.imread(sys.argv[2], cv.IMREAD_GRAYSCALE)

    ax[0].imshow(img1, cmap=plt.cm.get_cmap(name="cividis"), vmax=1)
    ax[0].set_title(sys.argv[1], fontdict={'fontsize': 11})

    ax[1].imshow(img2, cmap=plt.cm.get_cmap(name="cividis"), vmax=1)
    ax[1].set_title(sys.argv[2], fontdict={'fontsize': 11})


    ret, thresh = cv.threshold(img1, 127, 255,0)
    ret, thresh2 = cv.threshold(img2, 127, 255,0)
    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    cnt1 = contours[0]
    image, contours, hierarchy = cv.findContours(thresh2, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    cnt2 = contours[0]

    ret = cv.matchShapes(cnt1,cnt2,1,0.0)
    print("Similarity={:.2f}".format(1-ret))

    poly1 = cnt1.reshape(-1,2)
    ax[0].plot(poly1[:, 0], poly1[:, 1], linewidth=4)

    poly2 = cnt2.reshape(-1,2)
    ax[1].plot(poly2[:, 0], poly2[:, 1], linewidth=4)

    plt.show()
