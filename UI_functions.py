import numpy as np

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
        self.plot.axesdict["diff"] = self.diff_le.text()
    except ValueError:
        print("thats not a numbo dumbo")
    self.plot.update()
    self.plot._update_plot()

def xmin_setter(self):
    """this one still needs some work"""
    try:
        self.plot.axesdict["xmin"] = self.xmin_le.text()
    except ValueError:
        print("thats not a numbo dumbo")
    self.plot.update()
    self.plot._update_plot()

def ymin_setter(self):
    """this one still needs some work"""
    try:
        self.plot.axesdict["ymin"] = self.ymin_le.text()
    except ValueError:
        print("thats not a numbo dumbo")
    self.plot.update()
    self.plot._update_plot()
