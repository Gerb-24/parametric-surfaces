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
        self.plot.update()
        self.plot._update_plot()
        text.close()
