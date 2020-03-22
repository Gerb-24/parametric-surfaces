from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QLabel, QSlider, QHBoxLayout, QAction, QLineEdit, QCheckBox, QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

import point_selecter as sel
import UI_functions as UIfuncs
import bezierfuncs as bez
import file_menu_functions as fmf
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
import copy

#%matplotlib qt
#create new plot window
#matplotlib inline
#create plot in current console


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=8, dpi=100):
        self._figure = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, self._figure) # this gives the init from the super class FigureCanvas
        self.setParent(parent) # it has parent as parent, we want to give the mainwindow as parent later on

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class DraggablePlotExample(PlotCanvas):
    u""" An example of plot with draggable markers """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pointdictdict = {"longcurve": [{"node" : [-150,0], "handles" : [[-100,0]]},
                            {"node": [150,0], "handles": [[100,0]]}],
                            "shortcurvelist": [[{"node" : [-150,20], "handles" : [[-100,0]]},
                                                {"node": [150,0], "handles": [[100,0]]}]]}
        self.selected_curve = 0
        self.pointdict =    copy.deepcopy(self.pointdictdict["longcurve"])
        self.main_points = [self.pointdict[0]["node"],self.pointdict[1]["node"]]
        #self.pointlist = [[[100,250],[200,250],[300,250],[400,250]]]
        self.undolength = 10
        self.undolist = [copy.deepcopy(self.pointdict)]*self.undolength
        self.pointlist = []
        self.handle_expansion = []
        self.selected_node = 0

        # selection variables
        self.preselected = False
        self.selected = False
        self.dragging = False
        self.drag_x = False
        self.drag_y = False

        # for panning
        self.pan_x = None
        self.pan_y = None
        self.xpress = None
        self.ypress = None
        self.middle_dragging = True


        # background curve list
        self.bg_curve_list = []
        self.bg_pointlist = []

        self.next_curve_list = []
        self.prev_curve_list = []

        self._lines = None

        self.axesdict = {"diff": "1024", "xmin": "-512", "ymin": "-512"}
        self.x, self.y = None, None
        self._init_plot()
        self._update_plot()


    def _init_plot(self):
        #self._figure = plt.figure("Example plot")
        #axes = plt.subplot(1, 1, 1)
        self._axes = self._figure.add_subplot(111)
        self._axes.set_xlim(int(self.axesdict["xmin"]), int(self.axesdict["xmin"])+int(self.axesdict["diff"]))
        self._axes.set_ylim(int(self.axesdict["ymin"]), int(self.axesdict["ymin"])+int(self.axesdict["diff"]))
        self._axes.grid(which="both")

        self._figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._figure.canvas.mpl_connect('button_release_event', self._on_release)
        self._figure.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self._figure.canvas.mpl_connect('scroll_event', self._on_zoom)
        self.draw()


    def _update_plot(self):

        # # updating self.pointdict
        # self.pointdict = []
        # self.pointdict.append({"node": self.pointlist[0][0], "handles": [self.pointlist[0][1]]})
        # for i in range(len(self.pointlist)-1):
        #     self.pointdict.append({"node": self.pointlist[i][3], "handles": [self.pointlist[i][2],self.pointlist[i+1][1]]})
        # self.pointdict.append({"node": self.pointlist[len(self.pointlist)-1][3], "handles": [self.pointlist[len(self.pointlist)-1][2]]})

        self.pointlist = []
        self.pointlist.append([self.pointdict[0]["node"],self.pointdict[0]["handles"][0]])
        for i in range(1,(len(self.pointdict)-1)):
            self.pointlist[i-1].extend([self.pointdict[i]["handles"][0], self.pointdict[i]["node"]])
            self.pointlist.append([self.pointdict[i]["node"],self.pointdict[i]["handles"][1]])
        self.pointlist[(len(self.pointdict)-2)].extend([self.pointdict[len(self.pointdict)-1]["handles"][0], self.pointdict[len(self.pointdict)-1]["node"]])

        # updating self.main_points
        self.main_points = []
        for i in range(len(self.pointdict)):
            self.main_points.append(self.pointdict[i]["node"])

        # updating the plot
        self._axes.set_xlim(int(self.axesdict["xmin"]), int(self.axesdict["xmin"])+int(self.axesdict["diff"]))
        self._axes.set_ylim(int(self.axesdict["ymin"]), int(self.axesdict["ymin"])+int(self.axesdict["diff"]))
        t = np.linspace(0, 1, 200)
        self.x = bez.general_bezier_curve_range_x(t, self.pointlist)
        self.y = bez.general_bezier_curve_range_y(t, self.pointlist)

        # updating the handlespoints and the handles
        _point_drawing_list = []
        _handle_drawing_list = []

        if self.selected:
            node = self.pointdict[self.selected_node]["node"]
            for elem in self.pointdict[self.selected_node]["handles"]:
                _point_drawing_list.extend([*elem, 'g.'])
                _handle_drawing_list.extend([[node[0],elem[0]],[node[1],elem[1]],'g-'])

        # updating the main points
        _point_drawing_list.extend([*self.main_points[0], 'bo'])
        for a, b in self.main_points[1::]:
            _point_drawing_list.extend([a, b, 'b.'])

        # updating the total plot
        if  self._lines:
            for line in self._lines:
                self._axes.lines.remove(line)
        # if self.bg_curve_list != []:
        #     self._lines = self._axes.plot(*self.bg_curve_list,self.x, self.y, "b-", *_handle_drawing_list, *_point_drawing_list)
        # else:
        #     self._lines = self._axes.plot(self.x, self.y, "b-", *_handle_drawing_list, *_point_drawing_list)
        self._lines = self._axes.plot(*self.prev_curve_list, *self.next_curve_list, self.x, self.y, "b-", *_handle_drawing_list, *_point_drawing_list)

        self._figure.canvas.draw()


    def pdd_updater(self):
        if self.selected_curve:
            self.pointdictdict["shortcurvelist"][self.selected_curve-1] = copy.deepcopy(self.pointdict)
        else:
            self.pointdictdict["longcurve"] = copy.deepcopy(self.pointdict)


    def short_bg_setter(self):

        def next_setter(self):
            pointdict = self.pointdictdict["shortcurvelist"][self.selected_curve]
            main_points = []
            for i in range(len(pointdict)):
                main_points.append(pointdict[i]["node"])

            _point_drawing_list = []
            _point_drawing_list.extend([*main_points[0], 'ko'])
            for a, b in main_points[1::]:
                _point_drawing_list.extend([a, b, 'k.'])

            pointlist = []
            pointlist.append([pointdict[0]["node"],pointdict[0]["handles"][0]])
            for i in range(1,(len(pointdict)-1)):
                pointlist[i-1].extend([pointdict[i]["handles"][0], pointdict[i]["node"]])
                pointlist.append([pointdict[i]["node"], pointdict[i]["handles"][1]])
            pointlist[(len(pointdict)-2)].extend([pointdict[len(pointdict)-1]["handles"][0], pointdict[len(pointdict)-1]["node"]])

            t = np.linspace(0, 1, 200)
            x = bez.general_bezier_curve_range_x(t, pointlist)
            y = bez.general_bezier_curve_range_y(t, pointlist)
            new_next = [x, y, "k--", *_point_drawing_list]

            return new_next

        def prev_setter(self):
            pointdict = self.pointdictdict["shortcurvelist"][self.selected_curve-2]
            main_points = []
            for i in range(len(pointdict)):
                main_points.append(pointdict[i]["node"])

            _point_drawing_list = []
            _point_drawing_list.extend([*main_points[0], 'ro'])
            for a, b in main_points[1::]:
                _point_drawing_list.extend([a, b, 'r.'])

            pointlist = []
            pointlist.append([pointdict[0]["node"],pointdict[0]["handles"][0]])
            for i in range(1,(len(pointdict)-1)):
                pointlist[i-1].extend([pointdict[i]["handles"][0], pointdict[i]["node"]])
                pointlist.append([pointdict[i]["node"], pointdict[i]["handles"][1]])
            pointlist[(len(pointdict)-2)].extend([pointdict[len(pointdict)-1]["handles"][0], pointdict[len(pointdict)-1]["node"]])

            t = np.linspace(0, 1, 200)
            x = bez.general_bezier_curve_range_x(t, pointlist)
            y = bez.general_bezier_curve_range_y(t, pointlist)
            new_prev = [x, y, "r--", *_point_drawing_list]

            return new_prev

        if self.selected_curve == 0 or len(self.pointdictdict["shortcurvelist"]) == 1:
            self.prev_curve_list = []
            self.next_curve_list = []
        elif self.selected_curve == 1:
            self.prev_curve_list = []
            self.next_curve_list = next_setter(self)
        elif self.selected_curve == len(self.pointdictdict["shortcurvelist"]):
            self.prev_curve_list = prev_setter(self)
            self.next_curve_list = []
        else:
            self.prev_curve_list = prev_setter(self)
            self.next_curve_list = next_setter(self)


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
            #self.dragging = True
            self.newpoint = [e.xdata, e.ydata]
            """ this stores the current coordinates of the cursor"""

            if not self.selected:
                self.selected_node = sel.looper(self.main_points, self.newpoint)
                if self.selected_node == None:
                    return
                self.preselected = True
                #print(self.selected_node)

            elif self.selected:

                self.handle_expansion = self.main_points.copy()
                self.handle_expansion.extend(self.pointdict[self.selected_node]["handles"])
                self.selected_handle = sel.looper(self.handle_expansion, self.newpoint)
                if self.selected_handle == None:
                    self.selected = False
                    #print("selection off")
                else:
                    #print(self.selected_handle)
                    # the updating is in here
                    if self.drag_x:
                        self.newpoint = [self.newpoint[0],self.handle_expansion[self.selected_handle][1]]
                    elif self.drag_y:
                        self.newpoint = [self.handle_expansion[self.selected_handle][0], self.newpoint[1]]
                    if self.selected_handle < len(self.main_points):
                        if self.selected_handle == self.selected_node:
                            # here we update the handles
                            handle_update_list = []
                            for elem in self.pointdict[self.selected_handle]["handles"]:
                                handle_update_list.append(np.array(elem))
                            nodevec = np.array(self.pointdict[self.selected_node]["node"])
                            handle_diff_list = []
                            for elem in handle_update_list:
                                handle_diff_list.append(elem-nodevec)
                            newnode = np.array(self.newpoint)
                            handle_update_list = []
                            for elem in handle_diff_list:
                                newvec = newnode + elem
                                handle_update_list.append([newvec[0],newvec[1]])
                            self.pointdict[self.selected_handle]["handles"] = handle_update_list
                            self.pointdict[self.selected_handle]["node"] = self.newpoint
                        else:
                            self.selected_node = self.selected_handle
                    else:
                        handle_num = self.selected_handle-(len(self.main_points))
                        self.pointdict[self.selected_node]["handles"][handle_num] = self.newpoint
                        if len(self.pointdict[self.selected_node]["handles"]) == 2:
                            other_handle = 1-handle_num
                            nodevec = np.array(self.pointdict[self.selected_node]["node"])
                            vec = nodevec - np.array(self.newpoint)
                            newvec = nodevec + vec
                            self.pointdict[self.selected_node]["handles"][other_handle] = [newvec[0],newvec[1]]
                    self.dragging = True

            self.update()
            """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""
            self._update_plot()

        if e.button == 2:
            self.pan_x = self._axes.get_xlim()
            self.pan_y = self._axes.get_ylim()
            self.xpress, self.ypress = e.xdata, e.ydata
            self.middle_dragging = True


    def _on_release(self, event):
        u""" callback method for mouse release event
        :type event: MouseEvent
        """
        if event.button == 1 and event.inaxes in [self._axes]:
            if self.dragging:
                self.dragging = False
                self.drag_x = False
                self.drag_y = False
                self.undolist = self.undolist[1::]
                self.undolist.append(copy.deepcopy(self.pointdict))
            if self.preselected:
                self.selected = True
                self.preselected = False
                #print("selection on")
        if event.button == 2 and event.inaxes in [self._axes]:
            self.middle_dragging = False

        self.update()
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
        if e.xdata is None or e.ydata is None:
            return
        self.newpoint = [e.xdata, e.ydata]
        if e.button == 1 and self.dragging:
            """ this stores the current coordinates of the cursor"""
            if self.drag_x:
                self.newpoint = [self.newpoint[0],self.handle_expansion[self.selected_handle][1]]
            elif self.drag_y:
                self.newpoint = [self.handle_expansion[self.selected_handle][0], self.newpoint[1]]
            if self.selected_handle < len(self.main_points):

                # here we update the handles
                handle_update_list = []
                for elem in self.pointdict[self.selected_handle]["handles"]:
                    handle_update_list.append(np.array(elem))
                nodevec = np.array(self.pointdict[self.selected_node]["node"])
                handle_diff_list = []
                for elem in handle_update_list:
                    handle_diff_list.append(elem-nodevec)
                newnode = np.array(self.newpoint)
                handle_update_list = []
                for elem in handle_diff_list:
                    newvec = newnode + elem
                    handle_update_list.append([newvec[0],newvec[1]])
                self.pointdict[self.selected_handle]["handles"] = handle_update_list

                # here we update the node position
                self.selected_node = self.selected_handle
                self.pointdict[self.selected_handle]["node"] = self.newpoint



            else:
                handle_num = self.selected_handle-(len(self.main_points))
                self.pointdict[self.selected_node]["handles"][handle_num] = self.newpoint
                if len(self.pointdict[self.selected_node]["handles"]) == 2:
                    other_handle = 1-handle_num
                    nodevec = np.array(self.pointdict[self.selected_node]["node"])
                    vec = nodevec - np.array(self.newpoint)
                    newvec = nodevec + vec
                    self.pointdict[self.selected_node]["handles"][other_handle] = [newvec[0],newvec[1]]

            self.update()
            self._update_plot()
            """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""
        #print("works")
        if e.button == 2:

            if not self.middle_dragging: return
            dx = e.xdata - self.xpress
            dy = e.ydata - self.ypress
            self.pan_x -= dx
            self.pan_y -= dy
            self.axesdict["xmin"] = self.pan_x[0]
            self.axesdict["ymin"] = self.pan_y[0]
            self.update()
            self._update_plot()


    def _on_zoom(self, event):
        cur_xlim = self._axes.get_xlim()
        cur_ylim = self._axes.get_ylim()

        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        base_scale = 1.5

        if event.button == 'down':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'up':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            # print event.button

        diff = int(round((cur_xlim[1] - cur_xlim[0]) * scale_factor))

        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

        xmin = int(round(xdata - diff * (1-relx)))
        ymin = int(round(ydata - diff * (1-rely)))

        self.axesdict["xmin"] = str(xmin)
        self.axesdict["ymin"] = str(ymin)
        self.axesdict["diff"] = str(diff)
        # self._axes.set_xlim([, xdata + new_width * (relx)])
        # self._axes.set_ylim([ydata - new_width * (1-rely), ydata + new_height * (rely)])
        self.update()
        self._update_plot()


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
        self.width = 1000
        self.height = 800
        self.setGeometry(self.left, self.top, self.width, self.height)
        # it will start drawing the mainwindow at 400 400 with a width of 1000 and a height of 800

        self.title = 'b-curve draw window'
        self.setWindowTitle(self.title)

        self.initUI()
        # in here we put all the buttons and other UI elements


    def initUI(self):
        #plot 2d graph
        self.plot = DraggablePlotExample(self, width=8, height=8)
        self.plot.move(0,0)
        #plot 3d graph
        #self.plot2 = Surface3D(self, width=5, height=4)
        #self.plot2.move(600,0)
        self.vmfdict = {"height": 16*256, "xamount":16, "yamount": 16, "displength": 256, "dispwidth": 256}
        self.vmfmakenum = 0
        self.filename = ""
        self.control = False
        self.Ui_MainWindow()
        self.retranslateUi()


    def Ui_MainWindow(self):
        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(800, 23, 200, 781))
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
        self.groupBox_4.setGeometry(QtCore.QRect(20, 190, 151, 131))
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

        # this is the xmin lineedit
        self.xmin_le = QtWidgets.QLineEdit(self.groupBox_4)
        self.xmin_le.setObjectName("lineEdit_2")
        self.xmin_le.setText(str(self.plot.axesdict["xmin"]))
        self.xmin_le.returnPressed.connect(lambda: UIfuncs.xmin_setter(self))
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.xmin_le)


        self.label_3 = QtWidgets.QLabel(self.groupBox_4)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)

        # this is the ymin lineedit
        self.ymin_le = QtWidgets.QLineEdit(self.groupBox_4)
        self.ymin_le.setObjectName("lineEdit_3")
        self.ymin_le.setText(self.plot.axesdict["ymin"])
        self.ymin_le.returnPressed.connect(lambda: UIfuncs.ymin_setter(self))
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.ymin_le)

        # this is the difference
        self.diff_le = QtWidgets.QLineEdit(self.groupBox_4)
        self.diff_le.setObjectName("lineEdit")
        self.diff_le.setText(self.plot.axesdict["diff"])
        self.diff_le.returnPressed.connect(lambda: UIfuncs.diff_setter(self))
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.diff_le)

        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_5.setGeometry(QtCore.QRect(20, 340, 151, 231))
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_5)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_4 = QtWidgets.QLabel(self.groupBox_5)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)

        # this is the height
        self.height_le = QtWidgets.QLineEdit(self.groupBox_5)
        self.height_le.setObjectName("lineEdit_4")
        self.height_le.setText(str(self.vmfdict["height"]))
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.height_le)

        # this is the xamount
        self.xamount_le = QtWidgets.QLineEdit(self.groupBox_5)
        self.xamount_le.setObjectName("lineEdit_5")
        self.xamount_le.setText(str(self.vmfdict["xamount"]))
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.xamount_le)

        self.label_5 = QtWidgets.QLabel(self.groupBox_5)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)

        self.label_6 = QtWidgets.QLabel(self.groupBox_5)
        self.label_6.setObjectName("label_6")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)

        # this is the yamount
        self.yamount_le = QtWidgets.QLineEdit(self.groupBox_5)
        self.yamount_le.setObjectName("lineEdit_6")
        self.yamount_le.setText(str(self.vmfdict["yamount"]))
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.yamount_le)


        self.label_7 = QtWidgets.QLabel(self.groupBox_5)
        self.label_7.setObjectName("label_7")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_7)

        # this is the displength
        self.displength_le = QtWidgets.QLineEdit(self.groupBox_5)
        self.displength_le.setObjectName("lineEdit_7")
        self.displength_le.setText(str(self.vmfdict["displength"]))
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.displength_le)

        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setObjectName("label_8")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_8)

        # this is the dispwidth
        self.dispwidth_le = QtWidgets.QLineEdit(self.groupBox_5)
        self.dispwidth_le.setObjectName("lineEdit_8")
        self.dispwidth_le.setText(str(self.vmfdict["dispwidth"]))
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.dispwidth_le)

        # radio button 1
        self.radioButton_2 = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton_2.setObjectName("radioButton_2")
        self.radioButton_2.setChecked(True)
        self.radioButton_2.clicked.connect(lambda: UIfuncs.vmfmakenum_setter(self,0))
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.radioButton_2)

        # radio button 2
        self.radioButton = QtWidgets.QRadioButton(self.groupBox_5)
        self.radioButton.setObjectName("radioButton")
        self.radioButton.clicked.connect(lambda: UIfuncs.vmfmakenum_setter(self,1))
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.radioButton)

        # make vmf button
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_4.setGeometry(QtCore.QRect(50, 630, 91, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.vmf_maker)

        # background opening button
        self.opening_btn = QtWidgets.QPushButton(self.groupBox_2)
        self.opening_btn.setGeometry(QtCore.QRect(40, 590, 111, 28))
        self.opening_btn.setObjectName("pushButton_5")
        self.opening_btn.clicked.connect(lambda: UIfuncs.bg_setter(self))


        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # new file action
        self.actionNew = QtWidgets.QAction(self)
        self.actionNew.setObjectName("actionNew")
        self.actionNew.triggered.connect(lambda: fmf.newfile(self))

        # loading action
        self.actionOpen = QtWidgets.QAction(self)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.triggered.connect(lambda: fmf.load(self))

        # saving action
        self.actionSave = QtWidgets.QAction(self)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.triggered.connect(lambda: fmf.save(self))

        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Tools"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Curvepart tools"))

        self.pushButton.setText(_translate("MainWindow", "add curvepart"))
        self.pushButton.clicked.connect(lambda: UIfuncs.add_curvepart(self, self.plot.pointdict))

        self.pushButton_2.setText(_translate("MainWindow", "remove curvepart"))
        self.pushButton_2.clicked.connect(lambda: UIfuncs.remove_curvepart(self, self.plot.pointdict))

        self.pushButton_3.setText(_translate("MainWindow", "invert curve"))

        self.groupBox_4.setTitle(_translate("MainWindow", "Axes"))
        self.label.setText(_translate("MainWindow", "difference:"))
        self.label_2.setText(_translate("MainWindow", "x-min:"))
        self.label_3.setText(_translate("MainWindow", "y-min:"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Compile settings"))
        self.label_4.setText(_translate("MainWindow", "height:"))
        self.label_5.setText(_translate("MainWindow", "xamount:"))
        self.label_6.setText(_translate("MainWindow", "yamount:"))
        self.label_7.setText(_translate("MainWindow", "displength:"))
        self.label_8.setText(_translate("MainWindow", "dispwidth:"))
        self.radioButton_2.setText(_translate("MainWindow", "side"))
        self.radioButton.setText(_translate("MainWindow", "top"))
        self.pushButton_4.setText(_translate("MainWindow", "make vmf"))
        self.opening_btn.setText(_translate("MainWindow", "open background"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionNew.setText(_translate("MainWindow", "New"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))


    def vmf_maker(self):
        try:

            height, xamount, yamount, displength, dispwidth = int(self.height_le.text()), int(self.xamount_le.text()), int(self.yamount_le.text()), int(self.displength_le.text()), int(self.dispwidth_le.text())
            # bez.interpmaker(self.plot.bg_pointlist, self.plot.pointlist, height, xamount, yamount, displength, dispwidth)
            cm_list = [bez.curvemaker, bez.curvemaker2]
            #cm_list[self.vmfmakenum](self.plot.pointlist, height, xamount, yamount, displength, dispwidth)
            bez.along_normal_maker(self.plot.pointlist, height, xamount, yamount, displength, dispwidth)
            print("vmf is made!")
            #sys.exit()
        except ValueError:
            print("thats not a numbo dumbo")


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

        length = len(self.plot.pointdictdict["shortcurvelist"])
        for i,arg in curvekeys.items():
            """this will select curve i in curve mode"""
            if e.key() == arg:
                    if i <= length:
                        # saving the changed curve into the pointdictdict
                        self.plot.pdd_updater()

                        #changing the pointdict to the new selected curve
                        self.plot.selected_curve = i
                        self.plot.pointdict = copy.deepcopy(self.plot.pointdictdict["shortcurvelist"][i-1])
                        self.plot.short_bg_setter()
                        self.plot.update()
                        self.plot._update_plot()
        if e.key() == Qt.Key_Q:
            # saving the changed curve into the pointdictdict
            self.plot.pdd_updater()

            #changing the pointdict to the longcurve
            self.plot.selected_curve = 0
            self.plot.pointdict = copy.deepcopy(self.plot.pointdictdict["longcurve"])
            self.plot.short_bg_setter()
            self.plot.update()
            self.plot._update_plot()

        if not e.isAutoRepeat() and e.key() == Qt.Key_X and self.plot.dragging == True:
            self.plot.drag_x = not self.plot.drag_x
            self.plot.drag_y = False
            self.plot.update()
            self.plot._update_plot()

        if not e.isAutoRepeat() and e.key() == Qt.Key_Y and self.plot.dragging == True:
            self.plot.drag_y = not self.plot.drag_y
            self.plot.drag_x = False
            self.plot.update()
            self.plot._update_plot()

        if e.key() == Qt.Key_Control:
            self.control = True

        if e.key() == Qt.Key_S and self.control:
            fmf.q_save(self)
            self.control = False

        if e.key() == Qt.Key_Z and self.control:
            self.plot.pointdict = copy.deepcopy(self.plot.undolist[self.plot.undolength-2])

            self.plot.undolist = self.plot.undolist[:-1:]
            self.plot.undolist.insert(0,self.plot.undolist[0])
            self.control = False
            self.plot.update()
            self.plot._update_plot()

        if e.key() == Qt.Key_A:
            UIfuncs.add_curve(self, self.plot.pointdictdict)

        if e.key() == Qt.Key_D:
            UIfuncs.remove_curve(self, self.plot.pointdictdict)

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Control:
            self.control = False


def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    form = AppForm()
    # ui = Ui_MainWindow()
    # ui.setupUi(form)
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
