import sys

import matplotlib.patches as patches
import matplotlib.collections as collections
import matplotlib.pyplot as plt
import numpy as np

from skimage import io, morphology, measure

class Polygon():
    def __init__(self, points, center=[0, 0], snap=90):
        self.snap_angle = snap
        self.center = center
        self.points = points
        self.segment_vectors = None
        self.segment_lengths = None
        self.segment_unit_vectors = None
        self.segment_orientation = None
        self.segment_idx_maxlen = None

        self.update_properties()
        self.segment_done = np.zeros(len(self.segment_vectors))


    def update_properties(self):
        self.segment_vectors = np.diff(self.points, axis=0)
        self.segment_lengths = np.linalg.norm(self.segment_vectors, axis=1)
        self.segment_unit_vectors = np.divide(self.segment_vectors, np.array([self.segment_lengths, self.segment_lengths]).T)
        self.segment_orientation = np.degrees(np.arctan2(self.segment_unit_vectors[:, 0], self.segment_unit_vectors[:, 1]))+180
        self.segment_idx_maxlen = np.argmax(self.segment_lengths)

    def align_longest_edge(self):
        angle = self.segment_orientation[self.segment_idx_maxlen]
        snapped = np.round(angle/self.snap_angle)*self.snap_angle
        rotation = np.abs(angle)-snapped

        # make longest edge the first segment
        self.roll(-1*self.segment_idx_maxlen)

        # rotate polygon to snapped longest segment
        self.points = self._rotate2D(self.points, self.center, np.radians(rotation))
        self.update_properties()
        return self

    def iterate_segments(self):
        for n, vector in enumerate(self.segment_vectors):
            segment = np.array([self.points[n], self.points[n+1]])
            angle = self.segment_orientation[n]
            snapped = np.round(angle/self.snap_angle)*self.snap_angle
            rotation = (np.abs(angle)-snapped)
            segment = self._rotate2D(segment, segment[0]+(segment[1]-segment[0])/2, np.radians(rotation))
            self.points[n] = segment[0]
            self.points[n+1] = segment[1]
            self.update_properties()

        # close polygon
        self.points[0] = self.points[-1]
        self.update_properties()
        return self
    
    def get_points(self):
        return self.points

    def get_avg_deviation(self):
        rotation = []
        for n, vector in enumerate(self.segment_vectors):
            angle = self.segment_orientation[n]
            snapped = np.round(angle/self.snap_angle)*self.snap_angle
            rotation.append( np.abs((np.abs(angle)-snapped) ) )
        return(np.average(rotation))

    def force_snap(self):
        for n, vector in enumerate(self.segment_vectors):
            segment = np.array([self.points[n], self.points[n+1]])
            angle = self.segment_orientation[n]
            snapped = np.round(angle/self.snap_angle)*self.snap_angle
            rotation = (np.abs(angle)-snapped)
            segment = self._rotate2D(segment, segment[0], np.radians(rotation))
            self.points[n] = segment[0]
            self.points[n+1] = segment[1]
            self.update_properties()
        return self

    def roll(self, index=0):
        self.points = np.roll(self.points[:-1], index, axis=0)
        self.points = np.append(self.points, [self.points[0]], axis=0)
        return self

    def close_poly(self):
        # parallel lines, same orientation
        if np.abs(self.segment_orientation[0] - self.segment_orientation[-1]) < 1e-6:
            print("parallel lines, same orientation")
        # parallel lines, opposite orientation
        elif np.abs(self.segment_orientation[0] + self.segment_orientation[-1] - 360) < 1e-6:
            print("parallel lines, opposite orientation")
        else:
            intersect = self.get_intersect(self.points[0], self.points[1], self.points[-2], self.points[-1])
#            print(intersect)
#            if not (np.isinf(intersect[0]) or np.isinf(intersect[1])):
            self.points[0] = self.points[-1] = intersect
        return self

    def simplify(self):
        """ will remove unnecessary points on segments """
        # same orientation in consecutive segments means unnecessary points
        duplicates = np.add(np.where( np.abs(np.diff(self.segment_orientation)) < 1e-6), 1)
        self.points = np.delete(self.points, duplicates, axis=0)
        self.update_properties()
        return self

    @staticmethod
    def _rotate2D(points, center, angle):
        return np.dot(points - center, np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]))+center

    @staticmethod
    def get_intersect(a1, a2, b1, b2):
        """ 
        Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
        a1: [x, y] a point on the first line
        a2: [x, y] another point on the first line
        b1: [x, y] a point on the second line
        b2: [x, y] another point on the second line
        """
        s = np.vstack([a1,a2,b1,b2])        # s for stacked
        h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
        l1 = np.cross(h[0], h[1])           # get first line
        l2 = np.cross(h[2], h[3])           # get second line
        x, y, z = np.cross(l1, l2)          # point of intersection
        if z == 0:                          # lines are parallel
            return (np.inf, np.inf)
        return (x/z, y/z)

    
def Rotate2D(points, center, angle=np.pi/4):
    return np.dot(points - center, np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]))+center

fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(9.3, 6), sharex=True, sharey=True)
fig.subplots_adjust(left=0.03, right=0.97, hspace=0.3, wspace=0.05)
ax = axes.ravel()    
for a in ax.ravel():
    a.axis('off')
    a.set_aspect('equal')

# load test data
if len(sys.argv) > 1:
    source = io.imread(sys.argv[1], as_gray=True)
    #source = morphology.convex_hull_image(source)

    label_img = measure.label(source)


    # skimage uses row, column coordinate system where top-left = origin
    # matplotlib uses x,y coordinate system where top-left = origin
    ax[0].imshow(source, cmap=plt.cm.get_cmap(name="cividis"), vmax=1)
    ax[0].set_title("original shape and orientation", fontdict={'fontsize': 11})

    # extract polygon from shape
    shape = measure.approximate_polygon(measure.find_contours(source, 0.5)[0], tolerance=10)
    ax[1].imshow(source*0.4, cmap=plt.cm.get_cmap(name="cividis"), vmax=1)
    ax[1].quiver(shape[:,1][:-1], shape[:,0][:-1], shape[:,1][1:]-shape[:,1][:-1], shape[:,0][1:]-shape[:,0][:-1], 
        range(len(shape)), scale_units='xy', angles='xy', width=.01, scale=1, zorder=99,
        cmap=plt.cm.get_cmap(name="spring")
        )

    ax[1].set_title("polygon approximation and edges", fontdict={'fontsize': 11})

    # find global wall orientation
    region = measure.regionprops(label_img, coordinates="xy")[0]
    wall_orientation = np.array([
                            [[0, -region.major_axis_length/2],
                            [0,region.major_axis_length/2]], 
                            [[-region.minor_axis_length/2,0],
                            [region.minor_axis_length/2, 0]]
                            ])
    wall_orientation = Rotate2D(wall_orientation, [0,0], region.orientation)
    wall_orientation = wall_orientation + region.centroid
    ax[0].plot(wall_orientation[0][:, 1], wall_orientation[0][:, 0], '-r', linewidth=2.5)
    ax[0].plot(wall_orientation[1][:, 1], wall_orientation[1][:, 0], '-r', linewidth=2.5)
    ax[0].text(region.centroid[1], region.centroid[0], u'{:.2f}°'.format(np.degrees(region.orientation)))

    #polygon = Rotate2D(polygon, region.centroid, -region.orientation)
    # decomposition into segments (edges)
    polygon = Polygon(shape, region.centroid, snap=45)

    points = polygon.get_points()
    ax[2].plot(points[:, 1], points[:, 0], linewidth=2.5)
    ax[2].plot(points[:, 1], points[:, 0], 'or', markersize=3)
    ax[2].set_title("original polygon ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    polygon.align_longest_edge()
    points = polygon.get_points()
    ax[3].plot(points[:, 1], points[:, 0], linewidth=2.5)
    ax[3].plot(points[:, 1], points[:, 0], 'or', markersize=3)
    ax[3].set_title("align longest edge ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    polygon.iterate_segments()
    points = polygon.get_points()
    ax[4].plot(points[:, 1], points[:, 0], linewidth=2.5)
    ax[4].plot(points[:, 1], points[:, 0], 'or', markersize=3)
    ax[4].set_title("1st iteration ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    polygon.iterate_segments()
    points = polygon.get_points()
    ax[5].plot(points[:, 1], points[:, 0], linewidth=2.5)
    ax[5].plot(points[:, 1], points[:, 0], 'or', markersize=3)
    ax[5].set_title("2nd iteration ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    for _ in range(3):
        polygon.iterate_segments()
    points = polygon.get_points()
    ax[6].plot(points[:, 1], points[:, 0], linewidth=2.5)
    ax[6].plot(points[:, 1], points[:, 0], 'or', markersize=3)
    ax[6].set_title("5th iteration ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    for _ in range(5):
        polygon.iterate_segments()
    points = polygon.get_points()
    ax[7].plot(points[:, 1], points[:, 0], linewidth=2.5)
    ax[7].plot(points[:, 1], points[:, 0], 'or', markersize=3)
    ax[7].set_title("10th iteration ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})



    points = Polygon(shape, region.centroid, snap=45).align_longest_edge().force_snap().get_points()
    ax[8].imshow(source*0.4, cmap=plt.cm.get_cmap(name="cividis"), vmax=1)
    ax[8].plot(points[:, 1], points[:, 0], linewidth=2.5, color="red")
    ax[8].plot(points[:, 1], points[:, 0], 'o', color="white", markersize=1)
    ax[8].set_title("force-snapped only ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})
    ax[8].quiver(points[:,1][:-1], points[:,0][:-1], points[:,1][1:]-points[:,1][:-1], points[:,0][1:]-points[:,0][:-1], 
        range(len(points)), scale_units='xy', angles='xy', width=.01, scale=1, zorder=99,
        cmap=plt.cm.get_cmap(name="spring")
        )


    polygon.force_snap()
    polygon.close_poly()
    points = polygon.get_points()
    ax[9].imshow(source, cmap=plt.cm.get_cmap(name="cividis"))
    ax[9].plot(points[:, 1], points[:, 0], linewidth=2.5, color="red")
    ax[9].plot(points[:, 1], points[:, 0], 'o', color="white", markersize=1)
    ax[9].set_title("10th + force-snapped ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    polygon.simplify()
    points = polygon.get_points()
    ax[10].imshow(source, cmap=plt.cm.get_cmap(name="cividis"))
    ax[10].plot(points[:, 1], points[:, 0], linewidth=2.5, color="red")
    ax[10].plot(points[:, 1], points[:, 0], 'o', color="white", markersize=1)
    ax[10].set_title("simplified ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})

    points = polygon.get_points()
    #fig.patch.set_facecolor('#065da2')
    p = collections.PatchCollection([patches.Polygon(  np.roll(points, 1, axis=1), True)], edgecolor="cyan", linewidth=3)
    ax[11].add_collection(p)
    ax[11].set_title("final ({:.2f}°)".format(polygon.get_avg_deviation()), fontdict={'fontsize': 11})
    ax[11].set_facecolor('#065da2')

    #print(polygon)
    #current_shape = shape.get_shape()
    #ax[2].plot(current_shape[:, 1], current_shape[:, 0], linewidth=4)


# define objectives, constrains

# compute objective violations 

# initialize queue

# step-by-step transformation and queueing

# rotate to fit landscape orientation

plt.tight_layout()
plt.show()