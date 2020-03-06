from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QLabel, QSlider, QHBoxLayout, QAction, QLineEdit, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

import point_selecter as sel
import bezierfuncs as bez
import numpy as np


from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits import mplot3d
import math
import random
import sys
import random
from mpl_toolkits.mplot3d.axes3d import get_test_data

#%matplotlib qt
#create new plot window
#matplotlib inline
#create plot in current console


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=8, dpi=100):
        self._figure = Figure(figsize=(width, height), dpi=dpi)
        # self._axes = self._figure.add_subplot(111)

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
        self.pointlist = [[[155, 282], [135, 227], [185, 210], [213, 243]],
         [[213, 243], [253, 298], [281, 281], [284, 215]],
         [[284, 215], [283, 169], [320, 139], [348, 173]],
         [[348, 173], [368, 197], [390, 236], [345, 267]],
         [[345, 267], [305, 293], [309, 317], [350, 328]],
         [[350, 328], [392, 342], [388, 401], [334, 389]],
         [[334, 389], [294, 382], [299, 345], [243, 347]]]
        self.num = 1
        self.selected_curve = 1
        self.dragging = False
        self._init_plot()
        self._lines = None
        self.x, self.y = None, None
        self._update_plot()



    def _init_plot(self):
        #self._figure = plt.figure("Example plot")
        #axes = plt.subplot(1, 1, 1)
        self._axes = self._figure.add_subplot(111)
        self._axes.set_xlim(0, 500)
        self._axes.set_ylim(0, 500)
        self._axes.grid(which="both")

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.draw()

    def _update_plot(self):
        t = np.linspace(0, 1, 200)
        self.x = bez.general_bezier_curve_range_x(t, self.pointlist)
        self.y = bez.general_bezier_curve_range_y(t, self.pointlist)

        _point_drawing_list = []
        for a, b in self.pointlist[self.selected_curve-1]:
            _point_drawing_list.extend([a, b, 'r.'])
        _handle_drawing_list = []

        for i in range(0,4,2):
            _handle_drawing_list.extend(
                [[self.pointlist[self.selected_curve-1][i][0], self.pointlist[self.selected_curve-1][i + 1][0]],
                [self.pointlist[self.selected_curve-1][i][1], self.pointlist[self.selected_curve-1][i + 1][1]], 'g-'])

        # if not self.points:
        #     self._line.set_data([], [])
        # else:
        if  self._lines:
            for line in self._lines:
                self._axes.lines.remove(line)
        self._lines = self._axes.plot(self.x, self.y, "b-", *_handle_drawing_list, *_point_drawing_list)


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


class Surface3D(PlotCanvas):
    u""" showcase of 3d side pannel """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pointlist = [[[155, 282], [135, 227], [185, 210], [213, 243]]]
        self.num = 1
        self.selected_curve = 1
        self.dragging = False
        self._init_plot()
        self._lines = None


    def _init_plot(self):
        #self._figure = plt.figure("Example plot")
        #axes = plt.subplot(1, 1, 1)
        # self._axes = self._figure.axes(projection='3d')

        # self._axes.set_xlim(0, 500)
        # self._axes.set_ylim(0, 500)
        # self._axes.grid(which="both")


        self._axes = self._figure.add_subplot(1, 1, 1, projection='3d',label="topright")


        X, Y, Z = get_test_data(0.05)
        self._axes.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
        self._axes.set_title('Surface plot')
        # plt.show()


        self.draw()

    def update_plot(self,x,y,graph_depth=20):
        if not x or not y:
            return
        self._axes.clear()

        def get_r(val,grid):
            r = np.zeros(grid.shape)
            for i,ii in enumerate(grid):
                r[i,:] = val[:]
            return r
        u, v = np.mgrid[0:graph_depth:1, 0:len(x):1]
        X = get_r(x,u)
        Y = get_r(y,u)
        # z = np.ones(v.shape)
        Z = u
        self._axes.plot_wireframe(X, Y, Z, color="r")


        X = x*graph_depth #add multiple copies for depth
        Y = y*graph_depth #add multiple copies for depth
        Z = []
        for n in range(graph_depth):
            Z += [n]*len(x)

        # X, Y, Z = get_test_data(random.random())
        # self._axes.scatter(X, Y, Z)
        self._axes.set_title('Surface plot')
        # plt.show()


        self._figure.canvas.draw()


class AppForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 400
        self.top = 400
        self.title = 'b-curve draw window'
        self.width = 1000
        self.height = 800
        self.initUI()


    def initUI(self):
        # self.create_menu()
        # self.create_main_frame()
        # self.create_status_bar()
        #plot 2d graph
        self.plot = DraggablePlotExample(self, width=8, height=8)
        self.plot.move(0,0)
        #plot 3d graph
        #self.plot2 = Surface3D(self, width=5, height=4)
        #self.plot2.move(600,0)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:

         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())


    def on_draw(self):
        """ Redraws the figure
        """
        self.updateplot1()
        self.updateplot2()

    def updateplot1(self):
        self.plot._update_plot

    def updateplot2(self):
        self.plot2.update_plot(self.plot.x,self.plot.y,graph_depth=self.slider.value())


    def create_main_frame(self):
        self.main_frame = QWidget()

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
#        self.axes = self.fig.add_subplot(111)

        # Bind the 'pick' event for clicking on one of the bars
        #

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
        self.draw_button = QPushButton("&Draw 3D")
        self.draw_button.clicked.connect(self.updateplot2)


        slider_label = QLabel('3D depth (u):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.valueChanged.connect(self.on_draw)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [  self.draw_button, slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
#
#        load_file_action = self.create_action("&Save plot",
#            shortcut="Ctrl+S", slot=self.save_plot,
#            tip="Save the plot")
#        quit_action = self.create_action("&Quit", slot=self.close,
#            shortcut="Ctrl+Q", tip="Close the application")

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def keyPressEvent(self, e):
        # =============================================================================
        #create dictionary for keys in text
        # curvekeys = {}
        # Numberedkeys = 9
        # for i in range(Numberedkeys):
        #     curvekeys[i+1]=('Qt.Key_{}'.format(i+1))
        #
        # print(curvekeys)
        # =============================================================================
        curvekeys = {1: Qt.Key_1, 2: Qt.Key_2, 3: Qt.Key_3, 4: Qt.Key_4, 5: Qt.Key_5, 6: Qt.Key_6, 7: Qt.Key_7, 8: Qt.Key_8, 9: Qt.Key_9}
        #create dictionary for keys

        length = len(self.plot.pointlist)
        for i,arg in curvekeys.items():
            """this will select curve i in curve mode"""
            if e.key() == arg:
                    if i <= length:
                        self.plot.selected_curve = i
                        self.plot.update()
                        self.updateplot1

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(800, 0, 200, 800))
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 20, 151, 151))
        self.groupBox_3.setObjectName("groupBox_3")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_3)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 30, 112, 100))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_3.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout_3.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_3.addWidget(self.pushButton_3)
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_4.setGeometry(QtCore.QRect(20, 190, 151, 111))
        self.groupBox_4.setObjectName("groupBox_4")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_4)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox_4)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBox_4)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.label_3 = QtWidgets.QLabel(self.groupBox_4)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_3)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_5.setGeometry(QtCore.QRect(20, 320, 151, 111))
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_5)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_4 = QtWidgets.QLabel(self.groupBox_5)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_4)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_5)
        self.label_5 = QtWidgets.QLabel(self.groupBox_5)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_6 = QtWidgets.QLabel(self.groupBox_5)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.groupBox_5)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Tools"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Curvepart tools"))
        self.pushButton.setText(_translate("MainWindow", "add curvepart"))
        self.pushButton_2.setText(_translate("MainWindow", "remove curvepart"))
        self.pushButton_3.setText(_translate("MainWindow", "invert curve"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Axes"))
        self.label.setText(_translate("MainWindow", "difference:"))
        self.label_2.setText(_translate("MainWindow", "x-min:"))
        self.label_3.setText(_translate("MainWindow", "y-min:"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Compile settings"))
        self.label_4.setText(_translate("MainWindow", "height:"))
        self.label_5.setText(_translate("MainWindow", "xamount:"))
        self.label_6.setText(_translate("MainWindow", "yamount:"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

def main():
    app = QApplication(sys.argv)
    form = AppForm()
    ui = Ui_MainWindow()
    ui.setupUi(form)
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
