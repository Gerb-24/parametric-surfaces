from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon


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
        self._line =  None
        self._dragging_point = None
        self.points = {}

        self._init_plot()

    def _init_plot(self):
        #self._figure = plt.figure("Example plot")
        #axes = plt.subplot(1, 1, 1)
        self._axes.set_xlim(0, 100)
        self._axes.set_ylim(0, 100)
        self._axes.grid(which="both")

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.draw()

    def _update_plot(self):
        if not self.points:
            self._line.set_data([], [])
        else:
            x, y = zip(*sorted(self.points.items()))
            # Add new plot
            if not self._line:
                self._line, = self._axes.plot(x, y, "bo", markersize=10)
                pass
            # Update current plot
            else:
                self._line.set_data(x, y)
        self._figure.canvas.draw()

    def _add_point(self, x, y=None):
        if isinstance(x, MouseEvent):
            x, y = int(x.xdata), int(x.ydata)
        self.points[x] = y
        """this gives a problem, because if a point is created with the same
         x value, then the other point will be gone"""
        return x, y

    def _remove_point(self, x, _, event=None):
        if x in self.points:
            #if self._find_neighbor_point(event):
            self.points.pop(x)

    def _find_neighbor_point(self, event):
        u""" Find point around mouse position
        :rtype: ((int, int)|None)
        :return: (x, y) if there are any point around mouse else None
        """
        distance_threshold = 2.5
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

    def _on_click(self, event):
        u""" callback method for mouse click event
        :type event: MouseEvent
        """
        # left click
        if event.button == 1 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._dragging_point = point
            else:
                self._add_point(event)
            self._update_plot()
        # right click
        elif event.button == 3 and event.inaxes in [self._axes]:
            point = self._find_neighbor_point(event)
            if point:
                self._remove_point(*point)
                self._update_plot()

    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes] and self._dragging_point:
            self._dragging_point = None
            self._update_plot()

    def _on_motion(self, event):
        u""" callback method for mouse motion event
        :type event: MouseEvent
        """
        if not self._dragging_point:
            return
        if event.xdata is None or event.ydata is None:
            return
        self._remove_point(*self._dragging_point,event=event)
        self._dragging_point = self._add_point(event)
        self._update_plot()



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
