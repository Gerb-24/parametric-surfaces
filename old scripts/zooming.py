from matplotlib.pyplot import figure, show
import numpy

class ZoomPan:
    def __init__(self):
        self.middle_dragging = False
        self.pan_x = None
        self.pan_y = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None


    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                # print event.button

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            if event.button == 2:
                self.pan_x = ax.get_xlim()
                self.pan_y = ax.get_ylim()
                self.xpress, self.ypress = event.xdata, event.ydata
                self.middle_dragging = True

        def onRelease(event):
            self.middle_dragging = False
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.middle_dragging is False: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.pan_x -= dx
            self.pan_y -= dy
            ax.set_xlim(self.pan_x)
            ax.set_ylim(self.pan_y)

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion


fig = figure()

ax = fig.add_subplot(111, xlim=(0,1), ylim=(0,1), autoscale_on=False)

ax.set_title('Click to zoom')
x,y,s,c = numpy.random.rand(4,200)
s *= 200

ax.scatter(x,y,s,c)
scale = 1.1
zp = ZoomPan()
figZoom = zp.zoom_factory(ax, base_scale = scale)
figPan = zp.pan_factory(ax)
show()
