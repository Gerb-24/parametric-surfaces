import sys
import os
import bezierfuncs as bez
import ast
import parametric_surfaces_builder as ps
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QHBoxLayout


class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(self.size())
        with open("saved.txt", "r") as saved:
            self.pointlist = ast.literal_eval(saved.readline())
        """these will be the points around which we will construct the bezier curve
        so right now we only construct one bezier curve"""
        self.newpoint = [0, 0]  # this is just a starting value, so not very interesting
        self.num = 1
        self.dragging = False
        self.selected_curve = 1
        self.curve_mode = False
        # self.Init_UI()
        self.show()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and not self.curve_mode:
            self.dragging = True
            self.newpoint = [e.pos().x(), e.pos().y()]
            """ this stores the current coordinates of the cursor"""

            if self.num == 1 and not self.selected_curve == 1:
                self.pointlist[self.selected_curve - 2][3] = self.newpoint
            """if it is the first point then we also have to change the last point of the previous curve
            but if it is the first point of the first curve then we do not want to change a point from the -1th curve"""

            if self.num == 4 and not self.selected_curve == len(self.pointlist):
                self.pointlist[self.selected_curve][0] = self.newpoint
            """if it is the last point then we also have to change the last point of the following curve
            but if it is the last point of the last curve then we do not want to change a point from the last+1th curve"""

            self.pointlist[self.selected_curve-1][self.num-1] = self.newpoint
            """and here we change the selected point to the new point with the cursor position
            the selected point is given by num"""

            self.update()
            """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""


    def mouseMoveEvent(self,e):
        if (e.buttons() & Qt.LeftButton) & self.dragging:
            self.newpoint = [e.pos().x(), e.pos().y()]
            """ this stores the current coordinates of the cursor"""

            if self.num == 1 and not self.selected_curve == 1:
                self.pointlist[self.selected_curve - 2][3] = self.newpoint
            """if it is the first point then we also have to change the last point of the previous curve
            but if it is the first point of the first curve then we do not want to change a point from the -1th curve"""

            if self.num == 4 and not self.selected_curve == len(self.pointlist):
                self.pointlist[self.selected_curve][0] = self.newpoint
            """if it is the last point then we also have to change the last point of the following curve
            but if it is the last point of the last curve then we do not want to change a point from the last+1th curve"""

            self.pointlist[self.selected_curve-1][self.num-1] = self.newpoint
            """and here we change the selected point to the new point with the cursor position
            the selected point is given by num"""

            self.update()
            """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = False

    def keyPressEvent(self, e):
        length = len(self.pointlist)
        if e.key() == Qt.Key_1:
            """this will either select the curve 1 if it is in curve mode
            otherwise it will select point 1 of the selected curve"""
            if self.curve_mode:
                if 1 <= length:
                    self.selected_curve = 1
                    self.curve_mode = False
            else:
                self.num = 1
        elif e.key() == Qt.Key_2:
            """this will either select the curve 2 if it is in curve mode
            otherwise it will select point 2 of the selected curve"""
            if self.curve_mode:
                if 2 <= length:
                    self.selected_curve = 2
                    self.curve_mode = False
            else:
                self.num = 2
        elif e.key() == Qt.Key_3:
            """this will either select the curve 3 if it is in curve mode
            otherwise it will select point 3 of the selected curve"""
            if self.curve_mode:
                if 3 <= length:
                    self.selected_curve = 3
                    self.curve_mode = False
            else:
                self.num = 3
        elif e.key() == Qt.Key_4:
            """this will either select the curve 4 if it is in curve mode
            otherwise it will select point 4 of the selected curve"""
            if self.curve_mode:
                if 4 <= length:
                    self.selected_curve = 4
                    self.curve_mode = False
            else:
                self.num = 4
        elif e.key() == Qt.Key_5:
            """this will select curve 5 in curve mode"""
            if self.curve_mode:
                if 5 <= length:
                    self.selected_curve = 5
                    self.curve_mode = False
        elif e.key() == Qt.Key_6:
            """this will select curve 6 in curve mode"""
            if self.curve_mode:
                if 6 <= length:
                    self.selected_curve = 6
                    self.curve_mode = False
        elif e.key() == Qt.Key_7:
            """this will select curve 7 in curve mode"""
            if self.curve_mode:
                if 7 <= length:
                    self.selected_curve = 7
                    self.curve_mode = False
        elif e.key() == Qt.Key_8:
            """this will select curve 8 in curve mode"""
            if self.curve_mode:
                if 8 <= length:
                    self.selected_curve = 8
                    self.curve_mode = False
        elif e.key() == Qt.Key_9:
            """this will select curve 9 in curve mode"""
            if self.curve_mode:
                if 9 <= length:
                    self.selected_curve = 9
                    self.curve_mode = False
        elif e.key() == Qt.Key_A:
            print("a selected")
            """this will be adding a new curve"""
            lastpoint = self.pointlist[length-1][3]
            self.pointlist.append([lastpoint]*4)
            print(self.pointlist)
            """all new points will be created at the last point of the previous curve"""

        elif e.key() == Qt.Key_C:
            """this will make it go into curve mode"""
            self.curve_mode = True

        elif e.key() == Qt.Key_S:
            """this will save the created points to saved.txt as a preset to be loaded"""
            if os.path.exists("saved.txt"):
                os.remove("saved.txt")
            with open("saved.txt", "w") as text:
                text.write(str(self.pointlist))
        elif e.key() == Qt.Key_Space:
            print("enter is hit")
            print(self.pointlist)
            bez.curvemaker(self.pointlist)
            sys.exit()

        self.update()
        """update updates the whole GUI, which also runs the bezier plots with the new pointlist"""

    def paintEvent(self, ev):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)

        """here we define some pens and brushes"""
        redpen = QtGui.QPen(QtCore.Qt.red, 2)
        bluepen = QtGui.QPen(QtCore.Qt.blue, 2)
        blackpen = QtGui.QPen(QtCore.Qt.black, 1)
        brush = QtGui.QBrush(QtCore.Qt.black)

        qp.setPen(blackpen)
        """here the pen is set to a black pen with a thickness of 1"""
        qp.setBrush(brush)
        """here the brush is set to a black brush"""

        if not self.curve_mode:
            """so if we are not in curve mode, then the points and handles of the selected curve will be drawn"""
            selected_pointlist = self.pointlist[self.selected_curve-1]
            """these are the four points of our curve"""
            for i in range(len(selected_pointlist)):
                j = i+1
                qp.drawEllipse(selected_pointlist[i][0]-3, selected_pointlist[i][1]-3, 6, 6)
                """there are circles drawn at the places where the points are at"""
                qp.drawText(selected_pointlist[i][0] + 5, selected_pointlist[i][1] - 3, '%d' % j)
                """this creates a number at the top left of each circle"""
            qp.setPen(redpen)
            qp.drawLine(selected_pointlist[0][0], selected_pointlist[0][1], selected_pointlist[1][0],
                        selected_pointlist[1][1])
            qp.drawLine(selected_pointlist[2][0], selected_pointlist[2][1], selected_pointlist[3][0],
                        selected_pointlist[3][1])

        steps = 100
        """ this is the amount of steps we want to have in our bezier curve"""
        qp.setPen(bluepen)
        for i in range(len(self.pointlist)):
            oldPoint = (self.pointlist[i][0][0], self.pointlist[i][0][1])
            """ this is our starting point to create the bezier curve around"""

            for point in bez.bezier_curve_range(steps, self.pointlist[i]):
                qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])
                oldPoint = point
            if self.curve_mode:
                j = i+1
                halfpoint = bez.bezier(0.5,self.pointlist[i])
                qp.setPen(bluepen)
                qp.setFont(QtGui.QFont("arial", 10))
                qp.drawText(halfpoint[0], halfpoint[1], '%d' % j)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())
