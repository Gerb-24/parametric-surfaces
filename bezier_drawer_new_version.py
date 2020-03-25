from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QLabel, QSlider, QHBoxLayout, QAction, QLineEdit, QCheckBox, QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

import point_selecter as sel
import UI_functions as UIfuncs
import bezierfuncs as bez
import file_menu_functions as fmf
import along
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
        self._axes.grid(which="both", linestyle="--")

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
            self.axesdict["xmin"] = str(int(round(self.pan_x[0])))
            self.axesdict["ymin"] = str(int(round(self.pan_y[0])))
            self.update()
            self._update_plot()


    def _on_zoom(self, event):
        cur_xlim = self._axes.get_xlim()
        cur_ylim = self._axes.get_ylim()

        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        base_scale = 1.5

        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
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
        self.width = 1200
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
        self.vmfdict = {"height": 16*256, "radius": 256, "xamount":4, "yamount": 4, "displength": 256, "dispwidth": 256}
        self.vmfmakenum = 0
        self.filename = ""
        self.control = False
        self.Ui_MainWindow()


    def Ui_MainWindow(self):
        _translate = QtCore.QCoreApplication.translate

        def tools_grp_init(self, xstart, ystart, length, height):
            self.tools_grp = QtWidgets.QGroupBox(self)
            self.tools_grp.setGeometry(QtCore.QRect(xstart, ystart, length, height))
            self.tools_grp.setFlat(False)
            self.tools_grp.setCheckable(False)
            self.tools_grp.setObjectName("groupBox_2")

            self.tools_grp.setTitle(_translate("MainWindow", "Tools"))

            def cpt_grp_init(self, xstart, ystart, length, height):
                self.cptools_grp = QtWidgets.QGroupBox(self.tools_grp)
                self.cptools_grp.setGeometry(QtCore.QRect(xstart, ystart, length, height))
                self.cptools_grp.setObjectName("groupBox_3")
                self.layoutWidget = QtWidgets.QWidget(self.cptools_grp)
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

                self.cptools_grp.setTitle(_translate("MainWindow", "Curvepart tools"))

                self.pushButton.setText(_translate("MainWindow", "add curvepart"))
                self.pushButton.clicked.connect(lambda: UIfuncs.add_curvepart(self, self.plot.pointdict))

                self.pushButton_2.setText(_translate("MainWindow", "remove curvepart"))
                self.pushButton_2.clicked.connect(lambda: UIfuncs.remove_curvepart(self, self.plot.pointdict))

                self.pushButton_3.setText(_translate("MainWindow", "invert curve"))

            def axes_grp_init(self, xstart, ystart, length, height):

                self.axes_grp = QtWidgets.QGroupBox(self.tools_grp)
                self.axes_grp.setGeometry(QtCore.QRect(20, 190, 151, 161))
                self.axes_grp.setObjectName("groupBox_4")
                self.formLayout = QtWidgets.QFormLayout(self.axes_grp)
                self.formLayout.setObjectName("formLayout")
                # diff
                self.diff_le = QtWidgets.QLineEdit(self.axes_grp)
                self.diff_le.setObjectName("lineEdit")
                self.diff_le.setText(self.plot.axesdict["diff"])
                self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.diff_le)
                self.diff_lab = QtWidgets.QLabel(self.axes_grp)
                self.diff_lab.setObjectName("label")
                self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.diff_lab)
                # xmin
                self.xmin_lab = QtWidgets.QLabel(self.axes_grp)
                self.xmin_lab.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
                self.xmin_lab.setObjectName("label_2")
                self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.xmin_lab)
                self.xmin_le = QtWidgets.QLineEdit(self.axes_grp)
                self.xmin_le.setObjectName("lineEdit_2")
                self.xmin_le.setText(str(self.plot.axesdict["xmin"]))
                self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.xmin_le)
                # ymin
                self.ymin_lab = QtWidgets.QLabel(self.axes_grp)
                self.ymin_lab.setObjectName("label_3")
                self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.ymin_lab)
                self.ymin_le = QtWidgets.QLineEdit(self.axes_grp)
                self.ymin_le.setObjectName("lineEdit_3")
                self.ymin_le.setText(self.plot.axesdict["ymin"])
                self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.ymin_le)
                # get
                self.axesGetButton = QtWidgets.QPushButton(self.axes_grp)
                self.axesGetButton.setObjectName("pushButton_13")
                self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.axesGetButton)
                self.axesGetButton.clicked.connect(lambda: UIfuncs.axes_getter(self))
                #set
                self.axesSetButton = QtWidgets.QPushButton(self.axes_grp)
                self.axesSetButton.setObjectName("pushButton_14")
                self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.axesSetButton)
                self.axesSetButton.clicked.connect(lambda: UIfuncs.axes_setter(self))

                # axes group
                self.axes_grp.setTitle(_translate("MainWindow", "Axes"))
                self.diff_lab.setText(_translate("MainWindow", "difference:"))
                self.xmin_lab.setText(_translate("MainWindow", "x-min:"))
                self.ymin_lab.setText(_translate("MainWindow", "y-min:"))
                self.axesGetButton.setText(_translate("MainWindow", "Get"))
                self.axesSetButton.setText(_translate("MainWindow", "Set"))

            def sct_grp_init(self, xstart, ystart, length, height):
                self.shortCurveToolsGroup = QtWidgets.QGroupBox(self.tools_grp)
                self.shortCurveToolsGroup.setGeometry(QtCore.QRect(200, 20, 151, 151))
                self.shortCurveToolsGroup.setObjectName("groupBox_6")
                self.layoutWidget_2 = QtWidgets.QWidget(self.shortCurveToolsGroup)
                self.layoutWidget_2.setGeometry(QtCore.QRect(20, 30, 112, 100))
                self.layoutWidget_2.setObjectName("layoutWidget_2")
                self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
                self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_4.setObjectName("verticalLayout_4")
                self.addCurveButton = QtWidgets.QPushButton(self.layoutWidget_2)
                self.addCurveButton.setObjectName("pushButton_6")
                self.verticalLayout_4.addWidget(self.addCurveButton)
                self.removeCurveButton = QtWidgets.QPushButton(self.layoutWidget_2)
                self.removeCurveButton.setObjectName("pushButton_7")
                self.verticalLayout_4.addWidget(self.removeCurveButton)
                self.invAllCurveButton = QtWidgets.QPushButton(self.layoutWidget_2)
                self.invAllCurveButton.setObjectName("pushButton_8")
                self.verticalLayout_4.addWidget(self.invAllCurveButton)

                self.shortCurveToolsGroup.setTitle(_translate("MainWindow", "Shortcurve tools"))
                self.addCurveButton.setText(_translate("MainWindow", "add curve"))
                self.addCurveButton.clicked.connect(lambda: UIfuncs.add_curve(self, self.plot.pointdictdict))
                self.removeCurveButton.setText(_translate("MainWindow", "remove curve"))
                self.removeCurveButton.clicked.connect(lambda: UIfuncs.remove_curve(self, self.plot.pointdictdict))
                self.invAllCurveButton.setText(_translate("MainWindow", "invert all curves"))

            def newLineTab_init(self, xstart, ystart, length, height):

                self.NewLineTab = QtWidgets.QTabWidget(self.tools_grp)
                self.NewLineTab.setGeometry(QtCore.QRect(xstart, ystart, length, height))
                self.NewLineTab.setObjectName("tabWidget_2")

                def xLineTab_init():
                    self.tab_4 = QtWidgets.QWidget()
                    self.tab_4.setObjectName("tab_4")

                    self.frame_4 = QtWidgets.QFrame(self.tab_4)
                    self.frame_4.setGeometry(QtCore.QRect(10, 0, 171, 111))
                    self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
                    self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.frame_4.setObjectName("frame_4")
                    self.formLayout_6 = QtWidgets.QFormLayout(self.frame_4)
                    self.formLayout_6.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
                    self.formLayout_6.setObjectName("formLayout_6")

                    self.label_10 = QtWidgets.QLabel(self.frame_4)
                    self.label_10.setObjectName("label_10")
                    self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_10)

                    self.xStart_le = QtWidgets.QLineEdit(self.frame_4)
                    self.xStart_le.setObjectName("lineEdit_10")
                    self.xStart_le.setText("0")
                    self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.xStart_le)

                    self.label_11 = QtWidgets.QLabel(self.frame_4)
                    self.label_11.setObjectName("label_11")
                    self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_11)

                    self.xEnd_le = QtWidgets.QLineEdit(self.frame_4)
                    self.xEnd_le.setObjectName("lineEdit_11")
                    self.xEnd_le.setText("2000")
                    self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.xEnd_le)

                    self.label_12 = QtWidgets.QLabel(self.frame_4)
                    self.label_12.setObjectName("label_12")
                    self.formLayout_6.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_12)

                    self.xNodeNum_le = QtWidgets.QLineEdit(self.frame_4)
                    self.xNodeNum_le.setObjectName("lineEdit_12")
                    self.xNodeNum_le.setText("6")
                    self.formLayout_6.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.xNodeNum_le)

                    self.xNewCurve_btn = QtWidgets.QPushButton(self.tab_4)
                    self.xNewCurve_btn.setGeometry(QtCore.QRect(40, 120, 93, 28))
                    self.xNewCurve_btn.setObjectName("pushButton_5")
                    self.xNewCurve_btn.clicked.connect(lambda: UIfuncs.xLine_maker(self))

                    self.NewLineTab.addTab(self.tab_4, "")

                    self.label_10.setText(_translate("MainWindow", "x-start:"))
                    self.label_11.setText(_translate("MainWindow", "x-end:"))
                    self.label_12.setText(_translate("MainWindow", "node amount:"))
                    self.xNewCurve_btn.setText(_translate("MainWindow", "new curve"))
                    self.NewLineTab.setTabText(self.NewLineTab.indexOf(self.tab_4), _translate("MainWindow", "x-line"))

                def yLineTab_init():
                    self.tab_5 = QtWidgets.QWidget()
                    self.tab_5.setObjectName("tab_5")

                    self.frame_5 = QtWidgets.QFrame(self.tab_5)
                    self.frame_5.setGeometry(QtCore.QRect(10, 0, 171, 111))
                    self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
                    self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.frame_5.setObjectName("frame_5")

                    self.formLayout_7 = QtWidgets.QFormLayout(self.frame_5)
                    self.formLayout_7.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
                    self.formLayout_7.setObjectName("formLayout_7")

                    self.label_13 = QtWidgets.QLabel(self.frame_5)
                    self.label_13.setObjectName("label_13")
                    self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_13)

                    self.yStart_le = QtWidgets.QLineEdit(self.frame_5)
                    self.yStart_le.setObjectName("lineEdit_13")
                    self.yStart_le.setText("0")
                    self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.yStart_le)

                    self.label_14 = QtWidgets.QLabel(self.frame_5)
                    self.label_14.setObjectName("label_14")
                    self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_14)

                    self.yEnd_le = QtWidgets.QLineEdit(self.frame_5)
                    self.yEnd_le.setObjectName("lineEdit_14")
                    self.yEnd_le.setText("2000")
                    self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.yEnd_le)

                    self.label_15 = QtWidgets.QLabel(self.frame_5)
                    self.label_15.setObjectName("label_15")
                    self.formLayout_7.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_15)

                    self.yNodeNum_le = QtWidgets.QLineEdit(self.frame_5)
                    self.yNodeNum_le.setObjectName("lineEdit_15")
                    self.yNodeNum_le.setText("6")
                    self.formLayout_7.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.yNodeNum_le)

                    self.yNewCurve_btn = QtWidgets.QPushButton(self.tab_5)
                    self.yNewCurve_btn.setGeometry(QtCore.QRect(40, 120, 93, 28))
                    self.yNewCurve_btn.setObjectName("pushButton_11")
                    self.yNewCurve_btn.clicked.connect(lambda: UIfuncs.yLine_maker(self))

                    self.NewLineTab.addTab(self.tab_5, "")

                    self.label_13.setText(_translate("MainWindow", "y-start:"))
                    self.label_14.setText(_translate("MainWindow", "y-end:"))
                    self.label_15.setText(_translate("MainWindow", "node amount:"))
                    self.yNewCurve_btn.setText(_translate("MainWindow", "new curve"))
                    self.NewLineTab.setTabText(self.NewLineTab.indexOf(self.tab_5), _translate("MainWindow", "y-line"))

                def lineTab_init():
                    self.tab_6 = QtWidgets.QWidget()
                    self.tab_6.setObjectName("tab_6")

                    self.frame_6 = QtWidgets.QFrame(self.tab_6)
                    self.frame_6.setGeometry(QtCore.QRect(10, 0, 171, 111))
                    self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
                    self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.frame_6.setObjectName("frame_6")

                    self.formLayout_8 = QtWidgets.QFormLayout(self.frame_6)
                    self.formLayout_8.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
                    self.formLayout_8.setObjectName("formLayout_8")

                    self.label_16 = QtWidgets.QLabel(self.frame_6)
                    self.label_16.setObjectName("label_16")
                    self.formLayout_8.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_16)

                    self.lineEdit_16 = QtWidgets.QLineEdit(self.frame_6)
                    self.lineEdit_16.setObjectName("lineEdit_16")
                    self.formLayout_8.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_16)

                    self.label_17 = QtWidgets.QLabel(self.frame_6)
                    self.label_17.setObjectName("label_17")
                    self.formLayout_8.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_17)

                    self.lineEdit_17 = QtWidgets.QLineEdit(self.frame_6)
                    self.lineEdit_17.setObjectName("lineEdit_17")
                    self.formLayout_8.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_17)

                    self.label_18 = QtWidgets.QLabel(self.frame_6)
                    self.label_18.setObjectName("label_18")
                    self.formLayout_8.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_18)

                    self.lineEdit_18 = QtWidgets.QLineEdit(self.frame_6)
                    self.lineEdit_18.setObjectName("lineEdit_18")
                    self.formLayout_8.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_18)

                    self.pushButton_12 = QtWidgets.QPushButton(self.tab_6)
                    self.pushButton_12.setGeometry(QtCore.QRect(40, 120, 93, 28))
                    self.pushButton_12.setObjectName("pushButton_12")

                    self.NewLineTab.addTab(self.tab_6, "")

                    self.label_16.setText(_translate("MainWindow", "startlist:"))
                    self.label_17.setText(_translate("MainWindow", "endlist:"))
                    self.label_18.setText(_translate("MainWindow", "node amount:"))
                    self.pushButton_12.setText(_translate("MainWindow", "new curve"))
                    self.NewLineTab.setTabText(self.NewLineTab.indexOf(self.tab_6), _translate("MainWindow", "line"))

                xLineTab_init()
                yLineTab_init()
                lineTab_init()


            cpt_grp_init(self,20, 20, 151, 151)
            sct_grp_init(self, 200, 20, 151, 151)
            axes_grp_init(self, 20, 190, 151, 161)
            newLineTab_init(self,200, 190, 181, 191)

        def compset_grp_init(self, xstart, ystart, length, height):
            self.compset_grp = QtWidgets.QGroupBox(self)
            self.compset_grp.setGeometry(QtCore.QRect(xstart, ystart, length, height))
            self.compset_grp.setObjectName("groupBox")

            self.compset_grp.setTitle(_translate("MainWindow", "Compile Settings"))

            def comptab_init(self, xstart, ystart, length, height):
                self.comp_tab = QtWidgets.QTabWidget(self.compset_grp)
                self.comp_tab.setGeometry(QtCore.QRect(xstart, ystart, length, height))

                def alongTab():
                    self.comp_tab.setObjectName("tabWidget")
                    self.tab = QtWidgets.QWidget()
                    self.tab.setObjectName("tab")

                    self.alongVmf_btn = QtWidgets.QPushButton(self.tab)
                    self.alongVmf_btn.setGeometry(QtCore.QRect(40, 90, 91, 28))
                    self.alongVmf_btn.setObjectName("pushButton_4")
                    self.alongVmf_btn.clicked.connect(lambda: self.vmf_maker("along"))

                    self.frame_3 = QtWidgets.QFrame(self.tab)
                    self.frame_3.setGeometry(QtCore.QRect(20, 10, 141, 71))
                    self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
                    self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.frame_3.setObjectName("frame_3")

                    self.formLayout_5 = QtWidgets.QFormLayout(self.frame_3)
                    self.formLayout_5.setObjectName("formLayout_5")

                    self.radioButton_10 = QtWidgets.QRadioButton(self.frame_3)
                    self.radioButton_10.setObjectName("radioButton_10")
                    self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.radioButton_10)

                    self.radioButton_11 = QtWidgets.QRadioButton(self.frame_3)
                    self.radioButton_11.setObjectName("radioButton_11")
                    self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.radioButton_11)

                    self.comp_tab.addTab(self.tab, "")

                    self.alongVmf_btn.setText(_translate("MainWindow", "make vmf"))
                    self.radioButton_10.setText(_translate("MainWindow", "left"))
                    self.radioButton_11.setText(_translate("MainWindow", "right"))
                    self.comp_tab.setTabText(self.comp_tab.indexOf(self.tab), _translate("MainWindow", "along"))

                def heightTab():
                    self.tab_2 = QtWidgets.QWidget()
                    self.tab_2.setObjectName("tab_2")

                    self.heightVmf_btn = QtWidgets.QPushButton(self.tab_2)
                    self.heightVmf_btn.setGeometry(QtCore.QRect(40, 90, 91, 28))
                    self.heightVmf_btn.setObjectName("pushButton_9")
                    self.heightVmf_btn.clicked.connect(lambda: self.vmf_maker("height"))

                    self.frame = QtWidgets.QFrame(self.tab_2)
                    self.frame.setGeometry(QtCore.QRect(19, 10, 141, 71))
                    self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
                    self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.frame.setObjectName("frame")

                    self.formLayout_3 = QtWidgets.QFormLayout(self.frame)
                    self.formLayout_3.setObjectName("formLayout_3")

                    self.label_4 = QtWidgets.QLabel(self.frame)
                    self.label_4.setObjectName("label_4")
                    self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)

                    self.height_le = QtWidgets.QLineEdit(self.frame)
                    self.height_le.setObjectName("lineEdit_4")
                    self.height_le.setText("2000")
                    self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.height_le)

                    self.radioButton_5 = QtWidgets.QRadioButton(self.frame)
                    self.radioButton_5.setObjectName("radioButton_5")
                    self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.radioButton_5)

                    self.radioButton_6 = QtWidgets.QRadioButton(self.frame)
                    self.radioButton_6.setObjectName("radioButton_6")
                    self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.radioButton_6)

                    self.comp_tab.addTab(self.tab_2, "")

                    self.heightVmf_btn.setText(_translate("MainWindow", "make vmf"))
                    self.label_4.setText(_translate("MainWindow", "height:"))
                    self.radioButton_5.setText(_translate("MainWindow", "left"))
                    self.radioButton_6.setText(_translate("MainWindow", "right"))
                    self.comp_tab.setTabText(self.comp_tab.indexOf(self.tab_2), _translate("MainWindow", "height"))

                def tubeTab():
                    self.tab_3 = QtWidgets.QWidget()
                    self.tab_3.setObjectName("tab_3")

                    self.tubeVmf_btn = QtWidgets.QPushButton(self.tab_3)
                    self.tubeVmf_btn.setGeometry(QtCore.QRect(40, 90, 91, 28))
                    self.tubeVmf_btn.setObjectName("pushButton_10")
                    self.tubeVmf_btn.setText(_translate("MainWindow", "make vmf"))
                    self.tubeVmf_btn.clicked.connect(lambda: self.vmf_maker("tube"))


                    self.frame_2 = QtWidgets.QFrame(self.tab_3)
                    self.frame_2.setGeometry(QtCore.QRect(20, 10, 141, 71))
                    self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
                    self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
                    self.frame_2.setObjectName("frame_2")

                    self.formLayout_4 = QtWidgets.QFormLayout(self.frame_2)
                    self.formLayout_4.setObjectName("formLayout_4")

                    self.label_9 = QtWidgets.QLabel(self.frame_2)
                    self.label_9.setObjectName("label_9")
                    self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_9)

                    self.tubeRadius_le = QtWidgets.QLineEdit(self.frame_2)
                    self.tubeRadius_le.setObjectName("lineEdit_9")
                    self.tubeRadius_le.setText("256")
                    self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tubeRadius_le)

                    self.tubeInner_rb = QtWidgets.QRadioButton(self.frame_2)
                    self.tubeInner_rb.setObjectName("radioButton_7")
                    self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.tubeInner_rb)
                    self.tubeInner_rb.setText(_translate("MainWindow", "inner"))

                    self.tubeOuter_rb = QtWidgets.QRadioButton(self.frame_2)
                    self.tubeOuter_rb.setObjectName("radioButton_8")
                    self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.tubeOuter_rb)
                    self.tubeOuter_rb.setText(_translate("MainWindow", "outer"))

                    self.comp_tab.addTab(self.tab_3, "")
                    self.label_9.setText(_translate("MainWindow", "radius"))
                    self.comp_tab.setTabText(self.comp_tab.indexOf(self.tab_3), _translate("MainWindow", "tube"))

                alongTab()
                heightTab()
                tubeTab()

            def general_grp_init(self, xstart, ystart, length, height):
                self.general_grp = QtWidgets.QGroupBox(self.compset_grp)
                self.general_grp.setGeometry(QtCore.QRect(xstart, ystart, length, height))
                self.general_grp.setObjectName("groupBox_5")
                self.formLayout_2 = QtWidgets.QFormLayout(self.general_grp)
                self.formLayout_2.setObjectName("formLayout_2")

                self.general_grp.setTitle(_translate("MainWindow", "General "))

                # # height
                # self.height_le = QtWidgets.QLineEdit(self.groupBox_5)
                # self.height_le.setObjectName("lineEdit_4")
                # self.height_le.setText(str(self.vmfdict["height"]))
                # self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.height_le)

                # xamount
                self.xamount_le = QtWidgets.QLineEdit(self.general_grp)
                self.xamount_le.setObjectName("lineEdit_5")
                self.xamount_le.setText(str(self.vmfdict["xamount"]))
                self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.xamount_le)
                self.xamount_lab = QtWidgets.QLabel(self.general_grp)
                self.xamount_lab.setObjectName("label_5")
                self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.xamount_lab)
                # yamount
                self.yamount_lab = QtWidgets.QLabel(self.general_grp)
                self.yamount_lab.setObjectName("label_6")
                self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.yamount_lab)
                self.yamount_le = QtWidgets.QLineEdit(self.general_grp)
                self.yamount_le.setObjectName("lineEdit_6")
                self.yamount_le.setText(str(self.vmfdict["yamount"]))
                self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.yamount_le)
                # displength
                self.displength_lab = QtWidgets.QLabel(self.general_grp)
                self.displength_lab.setObjectName("label_7")
                self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.displength_lab)
                self.displength_le = QtWidgets.QLineEdit(self.general_grp)
                self.displength_le.setObjectName("lineEdit_7")
                self.displength_le.setText(str(self.vmfdict["displength"]))
                self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.displength_le)
                # dispwidth
                self.dispwith_lab = QtWidgets.QLabel(self.general_grp)
                self.dispwith_lab.setObjectName("label_8")
                self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.dispwith_lab)
                self.dispwidth_le = QtWidgets.QLineEdit(self.general_grp)
                self.dispwidth_le.setObjectName("lineEdit_8")
                self.dispwidth_le.setText(str(self.vmfdict["dispwidth"]))
                self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.dispwidth_le)

                # # radio button 1
                # self.radioButton_2 = QtWidgets.QRadioButton(self.general_grp)
                # self.radioButton_2.setObjectName("radioButton_2")
                # self.radioButton_2.setChecked(True)
                # self.radioButton_2.clicked.connect(lambda: UIfuncs.vmfmakenum_setter(self,0))
                # self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.radioButton_2)
                #
                # # radio button 2
                # self.radioButton = QtWidgets.QRadioButton(self.general_grp)
                # self.radioButton.setObjectName("radioButton")
                # self.radioButton.clicked.connect(lambda: UIfuncs.vmfmakenum_setter(self,1))
                # self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.radioButton)

                self.xamount_lab.setText(_translate("MainWindow", "xamount:"))
                self.yamount_lab.setText(_translate("MainWindow", "yamount:"))
                self.displength_lab.setText(_translate("MainWindow", "displength:"))
                self.dispwith_lab.setText(_translate("MainWindow", "dispwidth:"))

            comptab_init(self, 190, 20, 181, 161)
            general_grp_init(self, 20, 20, 151, 171)

        def menu_init(self):

            self.menubar = QtWidgets.QMenuBar(self)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 26))
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
            self.actionSave.triggered.connect(lambda: fmf.q_save(self))


            self.actionSaveAs = QtWidgets.QAction(self)
            self.actionSaveAs.setObjectName("actionSave")
            self.actionSaveAs.triggered.connect(lambda: fmf.save(self))
            # add the actionSave
            self.menuFile.addAction(self.actionNew)
            self.menuFile.addAction(self.actionOpen)
            self.menuFile.addAction(self.actionSave)
            self.menuFile.addAction(self.actionSaveAs)
            self.menubar.addAction(self.menuFile.menuAction())

            self.menuFile.setTitle(_translate("MainWindow", "File"))
            self.actionNew.setText(_translate("MainWindow", "New"))
            self.actionOpen.setText(_translate("MainWindow", "Open"))
            self.actionSave.setText(_translate("MainWindow", "Save"))
            self.actionSaveAs.setText(_translate("MainWindow", "Save As"))

        tools_grp_init(self, 800, 30, 391, 401)
        compset_grp_init(self, 800, 450, 381, 221)
        menu_init(self)

    def vmf_maker(self, mode):
        try:
            self.plot.pdd_updater()
            self.vmfdict = {"height": self.height_le.text(), "radius": self.tubeRadius_le.text(), "xamount": self.xamount_le.text(), "yamount": self.yamount_le.text(), "displength": self.displength_le.text(), "dispwidth": self.dispwidth_le.text()}
            # bez.interpmaker(self.plot.bg_pointlist, self.plot.pointlist, height, xamount, yamount, displength, dispwidth)
            #cm_list = [bez.curvemaker, bez.curvemaker2]
            #cm_list[self.vmfmakenum](self.plot.pointlist, height, xamount, yamount, displength, dispwidth)
            print("making the vmf")
            along.vmf_creater(self.plot.pointdictdict, self.vmfdict, mode)
            print("vmf is made!")
            #sys.exit()
        except ValueError:
            print("thats not a numbo hahaha")

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
    #app.setStyle(QStyleFactory.create('Fusion'))
    form = AppForm()
    # ui = Ui_MainWindow()
    # ui.setupUi(form)
    form.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
