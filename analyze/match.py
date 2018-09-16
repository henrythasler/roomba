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
    img1 = cv.GaussianBlur(img1,(31,31),0)
    img2 = cv.imread(sys.argv[2], cv.IMREAD_GRAYSCALE)

    ax[0].imshow(img1, cmap=plt.cm.get_cmap(name="cividis"))
    ax[0].set_title(sys.argv[1], fontdict={'fontsize': 11})

    ax[1].imshow(img2, cmap=plt.cm.get_cmap(name="cividis"))
    ax[1].set_title(sys.argv[2], fontdict={'fontsize': 11})

    kernel = np.ones((9, 9), np.uint8)

    ret, thresh = cv.threshold(cv.morphologyEx(img1, cv.MORPH_CLOSE, kernel), 127, 255, cv.THRESH_BINARY)
    ret, thresh2 = cv.threshold(cv.morphologyEx(img2, cv.MORPH_CLOSE, kernel), 127, 255, cv.THRESH_BINARY)
#    thresh1 = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
#    thresh2 = cv.morphologyEx(thresh2, cv.MORPH_CLOSE, kernel)


    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnt1 = contours[0]
    epsilon = 0.001*cv.arcLength(cnt1, False)
    cnt1 = cv.approxPolyDP(cnt1, epsilon, False)

    image, contours, hierarchy = cv.findContours(thresh2, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnt2 = contours[0]
    epsilon = 0.001*cv.arcLength(cnt2, False)
    cnt2 = cv.approxPolyDP(cnt2, epsilon, False)

    ret = cv.matchShapes(cnt1,cnt2,1,0.0)
    print("Similarity={:.2f}".format(1-ret))

    poly1 = cnt1.reshape(-1,2)
    ax[3].imshow(thresh, cmap=plt.cm.get_cmap(name="cividis"))
    ax[3].plot(poly1[:, 0], poly1[:, 1], linewidth=4)

    poly2 = cnt2.reshape(-1,2)
    ax[4].imshow(thresh2, cmap=plt.cm.get_cmap(name="cividis"))
    ax[4].plot(poly2[:, 0], poly2[:, 1], linewidth=4)

    plt.show()
