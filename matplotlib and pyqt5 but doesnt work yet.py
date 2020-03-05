from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
import point_selecter as sel
import bezierfuncs as bez
import numpy as np


from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import math
import random
import sys

#%matplotlib qt
#create new plot window
#matplotlib inline
#create plot in current console


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self._figure = Figure(figsize=(width, height), dpi=dpi)
        self._axes = self._figure.add_subplot(111)

        FigureCanvas.__init__(self, self._figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class DraggablePlotExample(PlotCanvas):
    u""" An example of plot with draggable markers """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pointlist = [[[155, 282], [135, 227], [185, 210], [213, 243]]]
        self.num = 1
        self.selected_curve = 1
        self.dragging = False
        self._lines = None
        self._init_plot()

    def _init_plot(self):
        #self._figure = plt.figure("Example plot")
        #axes = plt.subplot(1, 1, 1)
        self._axes.set_xlim(0, 500)
        self._axes.set_ylim(0, 500)
        self._axes.grid(which="both")

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.draw()

    def _update_plot(self):
        t = np.linspace(0, 1, 1000)
        x = bez.general_bezier_curve_range_x(t, self.pointlist)
        y = bez.general_bezier_curve_range_y(t, self.pointlist)

        _point_drawing_list = []
        for a, b in self.pointlist[0]:
            _point_drawing_list.extend([a, b, 'r.'])
        _handle_drawing_list = []

        for i in range(0,4,2):
            _handle_drawing_list.extend(
                [[self.pointlist[0][i][0], self.pointlist[0][i + 1][0]], [self.pointlist[0][i][1], self.pointlist[0][i + 1][1]], 'g-'])

        # if not self.points:
        #     self._line.set_data([], [])
        # else:
        if  self._lines:
            for line in self._lines:
                self._axes.lines.remove(line)
        self._lines = self._axes.plot(x, y, "b-", *_handle_drawing_list, *_point_drawing_list)


            # Update current plot
            # else:
            #     self._line.set_data(x, y)
        self._figure.canvas.draw()

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        distance_threshold = 10
        nearest_point = None
        min_distance = math.sqrt(2 * (100 ** 2))
        for x, y in self.points.items():
            distance = math.hypot(event.xdata - x, event.ydata - y)
            if distance < min_distance:
                min_distance = distance
                nearest_point = (x, y)
        if min_distance < distance_threshold:
            return nearest_point
        return None

    def _on_click(self, e):
        u""" callback method for mouse click event
        :type event: MouseEvent
        """
        # left click
        if e.button == 1 and e.inaxes in [self._axes]:
            self.dragging = True
            self.newpoint = [e.xdata, e.ydata]
            """ this stores the current coordinates of the cursor"""

            self.num = sel.fixed_looper(self.pointlist[self.selected_curve - 1], self.newpoint) + 1

            if self.num == 1 and not self.selected_curve == 1:
                self.pointlist[self.selected_curve - 2][3] = self.newpoint
            """if it is the first point then we also have to change the last point of the previous curve
            but if it is the first point of the first curve then we do not want to change a point from the -1th curve"""

            if self.num == 4 and not self.selected_curve == len(self.pointlist):
                self.pointlist[self.selected_curve][0] = self.newpoint
            """if it is the last point then we also have to change the last point of the following curve
            but if it is the last point of the last curve then we do not want to change a point from the last+1th curve"""

            if not self.num == 0:
                self.pointlist[self.selected_curve - 1][self.num - 1] = self.newpoint
                """and here we change the selected point to the new point with the cursor position
                the selected point is given by num"""

            self.update()
            """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""
            self._update_plot()
        # # right click
        # elif event.button == 3 and event.inaxes in [self._axes]:
        #     point = self._find_neighbor_point(event)
        #     if point:
        #         self._remove_point(*point)
        #         self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes] and self.dragging:
            self.dragging = False
            self._update_plot()

    def _on_motion(self, e):
        u""" callback method for mouse motion event
        :type event: MouseEvent
        """
        # if not self._dragging_point:
        #     return
        # if event.xdata is None or event.ydata is None:
        #     return
        # self._remove_point(*self._dragging_point,event=event)
        # self._dragging_point = self._add_point(event)
        # self._update_plot()
        if not self.dragging:
            return
        if e.xdata is None or e.ydata is None:
            return
        self.newpoint = [e.xdata, e.ydata]
        """ this stores the current coordinates of the cursor"""

        if self.num == 1 and not self.selected_curve == 1:
            self.pointlist[self.selected_curve - 2][3] = self.newpoint
        """if it is the first point then we also have to change the last point of the previous curve
        but if it is the first point of the first curve then we do not want to change a point from the -1th curve"""

        if self.num == 4 and not self.selected_curve == len(self.pointlist):
            self.pointlist[self.selected_curve][0] = self.newpoint
        """if it is the last point then we also have to change the last point of the following curve
        but if it is the last point of the last curve then we do not want to change a point from the last+1th curve"""

        if not self.num == 0:
            self.pointlist[self.selected_curve - 1][self.num - 1] = self.newpoint
        """and here we change the selected point to the new point with the cursor position
        the selected point is given by num"""

        self._update_plot()
        """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""


class App(QMainWindow):
    """Main application class containing the canvas and other UI elements"""

    def __init__(self):
        super().__init__()
        self.left = 400
        self.top = 400
        self.title = 'PyQt5 matplotlib example - pythonspot.com'
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.plot = DraggablePlotExample(self, width=5, height=4)
        self.plot.move(0,0)

        button = QPushButton('PyQt5 button', self)
        button.setToolTip('This is an example button')
        button.move(500,0)
        button.resize(140,100)

        self.show()


if __name__ == '__main__':
     app = QApplication(sys.argv)
     ex = App()
     sys.exit(app.exec_())
