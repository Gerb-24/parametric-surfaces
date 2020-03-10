import numpy as np

def add_curvepart(self, pointlist):
    length = len(pointlist)
    lastpoint_vec = np.array(pointlist[length - 1][3])
    prelastpoint_vec = np.array(pointlist[length-1][2])
    diff_vec = lastpoint_vec - prelastpoint_vec
    newlist = []
    for i in range(4):
        newlist.append([(lastpoint_vec+diff_vec*(i+1))[0],(lastpoint_vec+diff_vec*(i+1))[1]])
    pointlist.append(newlist)
    self.plot.selected_curve = length+1
    self.plot.update()
    self.plot._update_plot()

def remove_curvepart(self, pointlist):
    if len(self.plot.pointlist) == 1:
        return
    if self.plot.selected_curve == len(pointlist):
        self.plot.selected_curve = self.plot.selected_curve - 1
    pointlist.pop()
    self.plot.update()
    self.plot._update_plot()

def line_editor(text,changing_property, widget):
    """this one still needs some work"""
    try:
        changing_property = int(text)
    except ValueError:
        print("thats not a numbo dumbo")
    print(changing_property)
    widget.plot.update()
    widget.plot._update_plot()


def diff_setter(self):
    """this one still needs some work"""
    try:
        self.plot.diff = int(self.lineEdit.text())
    except ValueError:
        print("thats not a numbo dumbo")
    self.plot.update()
    self.plot._update_plot()

def xmin_setter(self):
    """this one still needs some work"""
    try:
        self.plot.xmin = int(self.lineEdit_2.text())
    except ValueError:
        print("thats not a numbo dumbo")
    self.plot.update()
    self.plot._update_plot()

def ymin_setter(self):
    """this one still needs some work"""
    try:
        self.plot.ymin = int(self.lineEdit_3.text())
    except ValueError:
        print("thats not a numbo dumbo")
    self.plot.update()
    self.plot._update_plot()
