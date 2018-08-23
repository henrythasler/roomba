import os
import sys

import matplotlib.pyplot as plt

import numpy as np

from skimage import io
from skimage.morphology import convex_hull_image, watershed, skeletonize_3d
from skimage import img_as_float
from skimage.color import rgb2gray
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage.feature import corner_harris, corner_subpix, corner_peaks, peak_local_max
from skimage import measure
from skimage import transform

from scipy import ndimage as ndi

def angle_rowwise(A, B):
    p1 = np.einsum('ij,ij->i',A,B)
    p2 = np.linalg.norm(A,axis=1)
    p3 = np.linalg.norm(B,axis=1)
    p4 = p1 / (p2*p3)
    return np.arccos(np.clip(p4,-1.0,1.0))       

#the function
def Rotate2D(pts,cnt,ang=np.pi/4):
    '''pts = {} Rotates points(nx2) about center cnt(2) by angle ang(1) in radian'''
    return np.dot(pts-cnt,np.array([[np.cos(ang),np.sin(ang)],[-np.sin(ang),np.cos(ang)]]))+cnt

if len(sys.argv) > 1:
    source = io.imread(sys.argv[1])
    source = rgb2gray(source)

    fig, axes = plt.subplots(2, 3, figsize=(7, 6), sharex=True, sharey=True)
    ax = axes.ravel()    
    for a in ax.ravel():
        a.axis('off')

    ax[0].imshow(source, interpolation='nearest')
    ax[0].set_title("Original image")

    chull = convex_hull_image(source)
    ax[1].imshow(img_as_float(chull), interpolation='nearest')
    ax[1].set_title("convex Hull and Orientation")

    label_img = measure.label(chull)
    regions = measure.regionprops(label_img, coordinates="rc")    

    for props in regions:
        y0, x0 = props.centroid
        orientation = props.orientation+np.pi/2
        print("Area: {}".format(props.area))
        x1 = x0 + np.cos(orientation) * 0.5 * props.major_axis_length
        y1 = y0 - np.sin(orientation) * 0.5 * props.major_axis_length
        x2 = x0 - np.sin(orientation) * 0.5 * props.minor_axis_length
        y2 = y0 - np.cos(orientation) * 0.5 * props.minor_axis_length

        ax[1].plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
        ax[1].plot((x0, x2), (y0, y2), '-r', linewidth=2.5)
        ax[1].plot(x0, y0, '.g', markersize=15)

        minr, minc, maxr, maxc = props.bbox
        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        #ax[1].plot(bx, by, '-b', linewidth=2.5)


    # Find contours at a constant value of 0.8
    contours = measure.find_contours(source, 0.5)
    ax[4].imshow(source)
    for n, contour in enumerate(contours[1:]):
        contour = measure.approximate_polygon(contour, tolerance=10)
        ax[4].plot(contour[:, 1], contour[:, 0], linewidth=4)
    ax[4].set_title("find_contours")


    ax[2].imshow(img_as_float(chull), interpolation='nearest')
    ax[2].set_title("convex_hull with contour")
    contours = measure.find_contours(chull, 0.5)
    for n, contour in enumerate(contours):
        contour = measure.approximate_polygon(contour, tolerance=10)
        print(contour)
#        ax[2].plot(contour[:, 1], contour[:, 0], linewidth=3)
        plt.set_cmap("cool")
        ax[2].quiver(contour[:,1][:-1], contour[:,0][:-1], contour[:,1][1:]-contour[:,1][:-1], contour[:,0][1:]-contour[:,0][:-1], range(len(contour)), scale_units='xy', angles='xy', width=.01, scale=1, zorder=99)
        ax[2].plot(contour[:, 1], contour[:, 0], '.r', markersize=6)
        plt.set_cmap("viridis")

        edges = np.diff(contour, axis=0)
        #print("Edges: {} {}".format(len(edges), edges))

        edge_lengths = np.linalg.norm(edges, axis=1)
        #print("Edge Lengths: {}".format(edge_lengths))

        longest_edge = np.argmax(edge_lengths)
        #print("Longest edge: index={} vector={} length={}".format(longest_edge, edges[longest_edge], edge_lengths[longest_edge]))

        unit_edges = np.divide(edges, np.array([edge_lengths, edge_lengths]).T)
        #print(unit_edges)

        #snap_angle_vectors = np.array([[1,0],[0,1]])# np.tile(np.array([1,0]), (len(edges),1))
        #print(snap_angle_vectors)
        #angles = np.arccos(np.clip(np.dot(snap_angle_vectors[:], unit_edges[:].T), -1.0, 1.0))
        #print(np.degrees(angles))

        angles = np.degrees(np.arctan2(unit_edges[:, 0], unit_edges[:, 1]))
        #print(angles)


    contours = measure.find_contours(source, 0.5)
    contour = measure.approximate_polygon(contours[0], tolerance=10)
    print(contour)
    plt.set_cmap("coolwarm")
    ax[4].quiver(contour[:,1][:-1], contour[:,0][:-1], contour[:,1][1:]-contour[:,1][:-1], contour[:,0][1:]-contour[:,0][:-1], range(len(contour)), scale_units='xy', angles='xy', width=.01, scale=1, zorder=99)
    ax[4].plot(contour[:, 1], contour[:, 0], '.r', markersize=6)
    plt.set_cmap("viridis")

    edges = np.diff(contour, axis=0)
    print("Edges: {} {}".format(len(edges), edges))

    edge_lengths = np.linalg.norm(edges, axis=1)
    print("Edge Lengths: {}".format(edge_lengths))

    longest_edge = np.argmax(edge_lengths)
    print("Longest edge: index={} vector={} length={}".format(longest_edge, edges[longest_edge], edge_lengths[longest_edge]))

    unit_edges = np.divide(edges, np.array([edge_lengths, edge_lengths]).T)
    print(unit_edges)

    #snap_angle_vectors = np.array([[1,0],[0,1]])# np.tile(np.array([1,0]), (len(edges),1))
    #print(snap_angle_vectors)
    #angles = np.arccos(np.clip(np.dot(snap_angle_vectors[:], unit_edges[:].T), -1.0, 1.0))
    #print(np.degrees(angles))

    angles = np.degrees(np.arctan2(unit_edges[:, 0], unit_edges[:, 1]))+180
    print(angles)
    print("\n")
    angles_snapped = np.round(angles/45)*45
    print(angles_snapped)

    rotations = np.abs(angles)-angles_snapped
    print("Rotation",rotations)


    ax[3].set_aspect('equal')
    ax[3].plot(contour[:, 1], contour[:, 0], '-b', linewidth=2)
    for n, edge in enumerate(edges):
        line = np.array([contour[n], contour[n+1]])    
        line = Rotate2D(line, line[0]+(line[1]-line[0])/2, np.radians(rotations[n]))
        ax[3].plot(line[:, 1], line[:, 0], '-r', linewidth=2)


#    line = np.array([contour[longest_edge], contour[longest_edge+1]])
#    print(line)
#    line = Rotate2D(line, line[0], np.radians(np.abs(angles[longest_edge])-angles_snapped[longest_edge]))
    #line = Rotate2D(line, line[0], np.radians(20))
#    print(line)
#    ax[3].plot(line[:, 1], line[:, 0], '-r', linewidth=2)

    plt.tight_layout()
    plt.show()