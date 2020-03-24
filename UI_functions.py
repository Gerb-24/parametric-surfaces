import numpy as np
import bezierfuncs as bez
from PyQt5.QtWidgets import QFileDialog
import ast
import ntpath
import copy

#####################
#CURVEPART FUNCTIONS#
#####################

def add_curvepart(self, pointdict):
    length = len(pointdict)
    lastpoint_vec = np.array(pointdict[length - 1]["node"])
    prelastpoint_vec = np.array(pointdict[length-1]["handles"][0])
    diff_vec = lastpoint_vec - prelastpoint_vec
    # newlist = []
    # for i in range(4):
    #     newlist.append([(lastpoint_vec+diff_vec*i)[0],(lastpoint_vec+diff_vec*i)[1]])
    # pointlist.append(newlist)
    pointdict[length-1]["handles"].append([(lastpoint_vec+diff_vec)[0],(lastpoint_vec+diff_vec)[1]])
    pointdict.append({"node": [(lastpoint_vec+diff_vec*3)[0],(lastpoint_vec+diff_vec*3)[1]], "handles": [[(lastpoint_vec+diff_vec*2)[0],(lastpoint_vec+diff_vec*2)[1]]]})
    self.plot.selected_node = length
    self.plot.update()
    self.plot._update_plot()

def remove_curvepart(self, pointdict):
    if len(self.plot.pointdict) == 2:
        return
    if self.plot.selected_node == len(pointdict)-1:
        self.plot.selected_node = self.plot.selected_node - 1
    pointdict.pop()
    pointdict[len(pointdict)-1]["handles"].pop()
    self.plot.update()
    self.plot._update_plot()

#################
#CURVE FUNCTIONS#
#################

def add_curve(self, pdd):
    self.plot.pdd_updater()
    scl = pdd["shortcurvelist"]
    length = len(scl)
    scl.append(scl[length-1])
    self.plot.selected_curve = length+1
    self.plot.pointdict = copy.deepcopy(scl[length])
    self.plot.short_bg_setter()
    self.plot.update()
    self.plot._update_plot()

def remove_curve(self, pdd):
    self.plot.pdd_updater()
    scl = pdd["shortcurvelist"]
    length = len(scl)
    if length == 1:
        return
    scl.pop()
    self.plot.selected_curve = length-1
    self.plot.pointdict = copy.deepcopy(scl[length-2])
    self.plot.short_bg_setter()
    self.plot.update()
    self.plot._update_plot()


################
#AXES FUNCTIONS#
################

def axes_setter(self):
    def diff_setter():
        """this one still needs some work"""
        try:
            self.plot.axesdict["diff"] = self.diff_le.text()
        except ValueError:
            print("thats not a numbo dumbo")
        self.plot.update()
        self.plot._update_plot()

    def xmin_setter():
        """this one still needs some work"""
        try:
            self.plot.axesdict["xmin"] = self.xmin_le.text()
        except ValueError:
            print("thats not a numbo dumbo")
        self.plot.update()
        self.plot._update_plot()

    def ymin_setter():
        """this one still needs some work"""
        try:
            self.plot.axesdict["ymin"] = self.ymin_le.text()
        except ValueError:
            print("thats not a numbo dumbo")
        self.plot.update()
        self.plot._update_plot()

    diff_setter()
    xmin_setter()
    ymin_setter()

def axes_getter(self):

    self.diff_le.setText(self.plot.axesdict["diff"])
    self.xmin_le.setText(self.plot.axesdict["xmin"])
    self.ymin_le.setText(self.plot.axesdict["ymin"])

#############################
#NEW CURVE PRESETS FUNCTIONS#
#############################
def pd_from_nodelist(nodelist):
    pointdict = []
    pointdict.append({"node": nodelist[0], "handles": [nodelist[1]]})
    for i in range(2,len(nodelist)-2, 3):
        pointdict.append({"node": nodelist[i+1],"handles":[nodelist[i], nodelist[i+2]]})
    pointdict.append({"node": nodelist[len(nodelist)-1], "handles": [nodelist[len(nodelist)-2]]})

    return pointdict

def xLine_maker(self):
    num = int(self.xNodeNum_le.text())
    xStart, xEnd = int(self.xStart_le.text()), int(self.xEnd_le.text())
    xDiff = xEnd-xStart
    nodelist = []
    ratio = (num-1)*3
    for i in range(ratio+1):
        nodelist.append([int(round(i*xDiff/ratio)),0])

    self.plot.pointdict = pd_from_nodelist(nodelist)
    self.plot.update()
    self.plot._update_plot()

def yLine_maker(self):
    num = int(self.yNodeNum_le.text())
    yStart, yEnd = int(self.yStart_le.text()), int(self.yEnd_le.text())
    yDiff = yEnd-yStart
    nodelist = []
    ratio = (num-1)*3
    for i in range(ratio+1):
        nodelist.append([0,int(round(i*yDiff/ratio))])

    self.plot.pointdict = pd_from_nodelist(nodelist)
    self.plot.update()
    self.plot._update_plot()

def vmfmakenum_setter(self, value):
    self.vmfmakenum = value

def bg_setter(self):
    if self.plot.bg_curve_list != []:
        self.plot.bg_curve_list = []
        self.plot.update()
        self.plot._update_plot()
        self.opening_btn.setText("open background")
        return
    filepath, _ = QFileDialog.getOpenFileName(self, "Load Background", "", "BEZ(*.bez)")
    if filepath == "":
        return
    with open(filepath, "r") as text:
        pointdict = ast.literal_eval(text.readline())

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

    self.plot.bg_pointlist = pointlist

    t = np.linspace(0, 1, 200)
    x = bez.general_bezier_curve_range_x(t, pointlist)
    y = bez.general_bezier_curve_range_y(t, pointlist)
    new_bg = [x, y, "k--", *_point_drawing_list]

    self.plot.bg_curve_list = new_bg
    self.plot.update()
    self.plot._update_plot()
    self.opening_btn.setText("close background")
