def add_curvepart(self, pointlist):
    length = len(pointlist)
    lastpoint = pointlist[length - 1][3]
    pointlist.append([lastpoint]*4)
    self.plot.update()
    self.plot._update_plot()

def remove_curvepart(self, pointlist):
    if self.plot.selected_curve == len(pointlist):
        self.plot.selected_curve = self.plot.selected_curve - 1
    pointlist.pop()
    self.plot.update()
    self.plot._update_plot()
