from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
    from PyQt6.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 1

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
    def __init__( self):
        super().__init__()
        self.pause = True

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self,line,color):
        self.showTangent(line,color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon,color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self,polygon):
        self.view.clearLines(polygon)

    def showText(self,text):
        self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
    def compute_hull( self, points, pause, view):
        self.pause = pause
        self.view = view
        assert( type(points) == list and type(points[0]) == QPointF )

        t1 = time.time()
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
        # I need to sort the points from smallest x to greatest x here
        sorted_points = sorted(points, key=lambda x: x.x())

        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        final_hull = self.find_hull(sorted_points , pause, view)
        t4 = time.time()
        final_hull_shape = [QLineF(final_hull[i], final_hull[(i+1) % len(final_hull)]) for i in range(len(final_hull))]

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(final_hull_shape, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

    def find_hull(self,points,pause,view):
        num_points = len(points)
        if num_points < 3:
            # need to put both hulls in clockwise order from leftmost point decreasing slope
            #sorted_points = self.sort_descending_slope(points)
            return points
        left_hull = self.find_hull(points[:num_points//2], pause, view)
        right_hull = self.find_hull(points[num_points//2:], pause, view)

        right_most_left_hull_index = left_hull.index(
            max(left_hull, key=lambda x: x.x()))

        left_most_right_hull_index = right_hull.index(
            min(right_hull, key=lambda x: x.x()))

        left_decreasing = False
        right_decreasing = False

        left_index = right_most_left_hull_index
        right_index = left_most_right_hull_index

        slope = self.find_slope(left_hull[right_most_left_hull_index], right_hull[left_most_right_hull_index])



        while left_decreasing == False or right_decreasing == False:
            left_decreasing = True
            right_decreasing = True


            while left_decreasing == True:
                left_index = (left_index - 1) % len(left_hull)
                next_slope = self.find_slope(left_hull[left_index],right_hull[right_index])

                if next_slope < slope:
                    slope = next_slope
                else:
                    left_index = (left_index + 1) % len(left_hull)
                    left_decreasing = False
            if(self.find_slope(left_hull[left_index],right_hull[(right_index + 1) % len(right_hull)]) <= slope):
                break

            while right_decreasing == True:
                right_index = (right_index + 1) % len(right_hull)
                next_slope = self.find_slope(left_hull[left_index],right_hull[right_index])

                if next_slope > slope:
                    slope = next_slope
                else:
                    right_decreasing = False
                    right_index = (right_index - 1) % len(right_hull)
            if(self.find_slope(left_hull[(left_index - 1) % len(left_hull)],right_hull[right_index]) >= slope):
                break

        top_left_tan_point = left_index
        right_tan_point_top = right_index

        #find the lower tangent
        left_decreasing = False
        right_decreasing = False
        left_index = right_most_left_hull_index
        right_index = left_most_right_hull_index

        slope = self.find_slope(left_hull[right_most_left_hull_index], right_hull[left_most_right_hull_index])

        while(left_decreasing == False or right_decreasing == False):
            left_decreasing = True
            right_decreasing = True
            while left_decreasing == True:
                left_index = (left_index + 1) % len(left_hull)
                next_slope = self.find_slope(left_hull[left_index],right_hull[right_index])
                if next_slope > slope:
                    slope = next_slope

                else:
                    left_index = (left_index - 1) % len(left_hull)
                    left_decreasing = False
            if(self.find_slope(left_hull[left_index],right_hull[(right_index - 1) % len(right_hull)]) >= slope):
                break

            while right_decreasing == True:
                right_index = (right_index - 1) % len(right_hull)
                next_slope = self.find_slope(left_hull[left_index],right_hull[right_index])

                if next_slope < slope:
                    slope = next_slope
                else:
                    right_decreasing = False
                    right_index = (right_index + 1) % len(right_hull)
            if(self.find_slope(left_hull[(left_index + 1) % len(left_hull)], right_hull[right_index]) <= slope):
                break

        lower_tan_point_left = left_index
        lower_tan_point_right = right_index
        solution_hull = []

        k = right_tan_point_top
        while k != lower_tan_point_right:
            solution_hull.append(right_hull[k])
            k = (k + 1) % len(right_hull)
        solution_hull.append(right_hull[lower_tan_point_right])

        j = lower_tan_point_left
        while j != top_left_tan_point:
            solution_hull.append(left_hull[j])
            j = (j + 1) % len(left_hull)
        solution_hull.append(left_hull[top_left_tan_point])

        return solution_hull


    def sort_descending_slope(self, points):
        slope_array = []
        slop_to_point = {}

        i = 1
        while i < len(points):
            slope = self.find_slope(points[0],points[i])
            slope_array.append(slope)
            slop_to_point[slope] = points[i]
            i = i + 1;

        slope_array.sort(reverse=True)
        slope_descending_order_points = []
        for i in range(len(slope_array)):
            slope_descending_order_points.append(slop_to_point[slope_array[i]])
        slope_descending_order_points.insert(0,points[0])
        return slope_descending_order_points




















    def find_slope(self,point1, point2):
            return (point2.y() - point1.y()) / (point2.x() - point1.x())
