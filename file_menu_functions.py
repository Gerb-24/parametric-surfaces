from PyQt5.QtWidgets import QFileDialog
import ast
import ntpath

def save(self):
    filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "BEZ(*.bez)")
    if filepath == "":
        return
    self.vmfdict = {"height": self.height_le.text(), "xamount": self.xamount_le.text(), "yamount": self.yamount_le.text(), "displength": self.displength_le.text(), "dispwidth": self.dispwidth_le.text()}

    with open(filepath, "w") as text:
        text.writelines([str(self.plot.pointdict)+"\n",str(self.vmfdict)+"\n"])
        text.close()
    self.title = 'b-curve draw window : ' + ntpath.basename(filepath)
    self.setWindowTitle(self.title)

def load(self):
    filepath, _ = QFileDialog.getOpenFileName(self, "Load File", "", "BEZ(*.bez)")
    if filepath == "":
        return
    with open(filepath, "r") as text:
        self.plot.pointdict= ast.literal_eval(text.readline())
        self.vmfdict = ast.literal_eval(text.readline())
        newdict = {self.height_le: "height", self.xamount_le: "xamount", self.yamount_le: "yamount", self.displength_le: "displength", self.dispwidth_le: "dispwidth"}
        for le, le_text in newdict.items():
            le.setText(self.vmfdict[le_text])

        # # updating self.pointdict
        # self.plot.pointdict = []
        # self.plot.pointdict.append({"node": self.plot.pointlist[0][0], "handles": [self.plot.pointlist[0][1]]})
        # for i in range(len(self.plot.pointlist)-1):
        #     self.plot.pointdict.append({"node": self.plot.pointlist[i][3], "handles": [self.plot.pointlist[i][2],self.plot.pointlist[i+1][1]]})
        # self.plot.pointdict.append({"node": self.plot.pointlist[len(self.plot.pointlist)-1][3], "handles": [self.plot.pointlist[len(self.plot.pointlist)-1][2]]})

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
