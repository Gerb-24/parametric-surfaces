from PyQt5.QtWidgets import QFileDialog
import ast
import ntpath

def save(self):

    #updating the pointdictdict
    self.plot.pdd_updater()

    filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "BEZ(*.bez)")
    if filepath == "":
        return
    self.filename = filepath
    self.vmfdict = {"height": self.height_le.text(), "radius": self.tubeRadius_le.text(), "xamount": self.xamount_le.text(), "yamount": self.yamount_le.text(), "displength": self.displength_le.text(), "dispwidth": self.dispwidth_le.text()}
    self.plot.axesdict = {"diff": self.diff_le.text(), "xmin": self.xmin_le.text(), "ymin": self.ymin_le.text()}
    with open(filepath, "w") as text:
        text.writelines([str(self.plot.pointdictdict)+"\n", str(self.vmfdict)+"\n", str(self.plot.axesdict)+"\n"])
        text.close()
    self.title = 'b-curve draw window : ' + ntpath.basename(filepath)
    self.setWindowTitle(self.title)

def q_save(self):
    #updating the pointdictdict
    self.plot.pdd_updater()

    if self.filename == "":
        save(self)
        return
    self.vmfdict = {"height": self.height_le.text(), "radius":self.tubeRadius_le.text(), "xamount": self.xamount_le.text(), "yamount": self.yamount_le.text(), "displength": self.displength_le.text(), "dispwidth": self.dispwidth_le.text()}
    self.plot.axesdict = {"diff": self.diff_le.text(), "xmin": self.xmin_le.text(), "ymin": self.ymin_le.text()}
    with open(self.filename, "w") as text:
        text.writelines([str(self.plot.pointdictdict)+"\n", str(self.vmfdict)+"\n", str(self.plot.axesdict)+"\n"])
        text.close()


def load(self):
    filepath, _ = QFileDialog.getOpenFileName(self, "Load File", "", "BEZ(*.bez)")
    if filepath == "":
        return
    self.filename = filepath
    with open(filepath, "r") as text:
        self.plot.pointdictdict= ast.literal_eval(text.readline())
        self.vmfdict = ast.literal_eval(text.readline())
        self.plot.axesdict = ast.literal_eval(text.readline())

        # updating the values in the toolbar
        newvmfdict = {self.height_le: "height", self.tubeRadius_le: "radius", self.xamount_le: "xamount", self.yamount_le: "yamount", self.displength_le: "displength", self.dispwidth_le: "dispwidth"}
        newaxesdict = {self.diff_le: "diff", self.xmin_le: "xmin", self.ymin_le: "ymin"}
        for le, le_text in newvmfdict.items():
            le.setText(self.vmfdict[le_text])
        for le, le_text in newaxesdict.items():
            le.setText(self.plot.axesdict[le_text])

        # updating the plot
        self.plot.selected_node = 0
        self.plot.selected_curve = 0
        self.plot.pointdict = self.plot.pointdictdict["longcurve"]
        self.plot.update()
        self.plot._update_plot()
        text.close()
    self.title = 'b-curve draw window : ' + ntpath.basename(filepath)
    self.setWindowTitle(self.title)

def newfile(self):
    self.plot.pointlist = [[[100,250],[200,250],[300,250],[400,250]]]

    # updating self.pointdict
    self.plot.pointdict = []
    self.plot.pointdict.append({"node": self.plot.pointlist[0][0], "handles": [self.plot.pointlist[0][1]]})
    for i in range(len(self.plot.pointlist)-1):
        self.plot.pointdict.append({"node": self.plot.pointlist[i][3], "handles": [self.plot.pointlist[i][2],self.plot.pointlist[i+1][1]]})
    self.plot.pointdict.append({"node": self.plot.pointlist[len(self.plot.pointlist)-1][3], "handles": [self.plot.pointlist[len(self.plot.pointlist)-1][2]]})

    self.plot.update()
    self.plot._update_plot()
