from PyQt5.QtWidgets import QFileDialog
import ast

def save(self):
    filepath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "BEZ(*.bez)")
    if filepath == "":
        return
    with open(filepath, "w") as text:
        text.write(str(self.plot.pointlist))
        text.close()

def load(self):
    filepath, _ = QFileDialog.getOpenFileName(self, "Load File", "", "BEZ(*.bez)")
    if filepath == "":
        return
    with open(filepath, "r") as text:
        self.plot.pointlist = ast.literal_eval(text.readline())

        # updating self.pointdict
        self.plot.pointdict = []
        self.plot.pointdict.append({"node": self.plot.pointlist[0][0], "handles": [self.plot.pointlist[0][1]]})
        for i in range(len(self.plot.pointlist)-1):
            self.plot.pointdict.append({"node": self.plot.pointlist[i][3], "handles": [self.plot.pointlist[i][2],self.plot.pointlist[i+1][1]]})
        self.plot.pointdict.append({"node": self.plot.pointlist[len(self.plot.pointlist)-1][3], "handles": [self.plot.pointlist[len(self.plot.pointlist)-1][2]]})

        self.plot.update()
        self.plot._update_plot()
        text.close()

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
