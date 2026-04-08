import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

class PlotDrawer():
    line_types = ["k-", "k--", "k:", "k-."]
    @staticmethod
    def drawSinglePlot(xs, ys, figure: Figure):
        ax = figure.axes[0]
        ax.clear()
        ax.plot(xs, ys)

    @staticmethod
    def drawMultiPlotMixed(xs, ys, figure: Figure):
        ax = figure.axes[0]
        ax.clear()
        for i in range(len(xs)):
            ax.plot(xs, ys, PlotDrawer.line_types[i%len(PlotDrawer.line_types)])

    @staticmethod
    def drawPlotsFirstLab(xs, ys, figure: Figure, legend, axes_names, title):
        ax = figure.axes[0]
        ax.clear()
        ax.grid(True)
        ax.plot(xs[0], ys[0], 'b-', label=legend[0])
        ax.plot(xs[1], ys[1], 'or', label=legend[1])
        ax.plot(xs[2], ys[2], 'g--', label=legend[2])
        ax.set_title(title)
        ax.set_xlabel(axes_names[0])
        ax.set_ylabel(axes_names[1])
        ax.legend()

    @staticmethod
    def drawPlotsSecondLab(xs, ys, figure: Figure, legend, axes_names, title):
        ax = figure.axes[0]
        ax.clear()
        ax.grid(True)
        ax.plot(xs[0], ys[0], 'o--b', label=legend[0])
        ax.plot(xs[1], ys[1], '^:g', label=legend[1])
        ax.set_title(title)
        ax.set_xlabel(axes_names[0])
        ax.set_ylabel(axes_names[1])
        ax.legend()
    
