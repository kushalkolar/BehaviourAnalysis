from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None,width = 4, height = 3, dpi=100):
        
        fig = Figure(figsize = (width, height),dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
#        self.plot()

    def plot(self):
        data = np.sin(np.linspace(0, 6*np.pi, 1000))*np.random.normal(1,0.1,1000)
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()
        self.show()
    
    def boxplot(self):
        group1 = np.random.normal(10,4,1000)
        group2 = np.random.normal(15, 3, 1000)
        ax = self.figure.add_subplot(111)
        ax.set_title("Boxplot Example")
        ax.violinplot([group1, group2])
        self.draw()
        self.show()
    
    def clear(self):
        self.axes.cla()
        self.draw()




class PlotWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.canvas = PlotCanvas(parent = self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    def draw(self):
        self.canvas.draw()

    def plot(self, x, y, xname = "X", yname = "Y", plot_title = False, color = "b", linewidth = 2, alpha = 1, clear_axis = True):
        if clear_axis:
            self.canvas.clear()
            ax = self.canvas.figure.add_subplot(111)
        else:
            ax = self.canvas.figure.gca()
        ax.plot(x, y, color = color, lw = linewidth, alpha = alpha)
        ax.set_xlabel(xname)
        ax.set_ylabel(yname)
        if not plot_title:
            ax.set_title(yname + " vs " + xname)
        else:
            ax.set_title(plot_title)
        self.canvas.figure.tight_layout()
        self.draw()

        
