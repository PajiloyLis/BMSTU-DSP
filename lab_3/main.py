import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt6.uic import loadUi
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from signalGenerator import SignalGenerator
from plotDrawer import PlotDrawer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('lab.ui', self)
        self.dx = self.dxdoubleSpinBox.value()
        self.sigma = self.gaussSigmadoubleSpinBox.value()
        self.l = self.rectLdoubleSpinBox.value()
        self.signalGenerator = SignalGenerator(-5., 5.)
        self.setupPlotWidget(self.gaussXGaussPlotwidget)
        self.setupPlotWidget(self.rectXRectPlotwidget)
        self.setupPlotWidget(self.rectXGaussPlotwidget)
        self.rectLdoubleSpinBox.valueChanged.connect(self.rectLValueCangedHandler)
        self.dxdoubleSpinBox.valueChanged.connect(self.dxValueChangedHandler)
        self.gaussSigmadoubleSpinBox.valueChanged.connect(self.gaussSigmaValueChangedHandler)

    def rectLValueCangedHandler(self):
        self.l = self.rectLdoubleSpinBox.value()
        discrete_rect_x, discrete_rect_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        discrete_gauss_x, discrete_gauss_y=self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        rect_rect_conv_x, rect_rect_conv_y = self.signalGenerator.frequenceConvolution(discrete_rect_y, discrete_rect_y, self.dx)
        rect_gauss_conv_x, rect_gauss_conv_y = self.signalGenerator.frequenceConvolution(discrete_rect_y, discrete_gauss_y, self.dx)
        PlotDrawer.drawPlotThirdLab(rect_rect_conv_x, rect_rect_conv_y, self.rectXRectPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка двух прямоугольных сигналов")
        self.rectXRectPlotwidget.canvas.draw()
        PlotDrawer.drawPlotThirdLab(rect_gauss_conv_x, rect_gauss_conv_y, self.rectXGaussPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка прямоугольного и гауссова сигналов")
        self.rectXGaussPlotwidget.canvas.draw()
        
    def gaussSigmaValueChangedHandler(self):
        self.sigma = self.gaussSigmadoubleSpinBox.value()
        discrete_rect_x, discrete_rect_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        discrete_gauss_x, discrete_gauss_y=self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        gauss_gauss_conv_x, gauss_gauss_conv_y = self.signalGenerator.frequenceConvolution(discrete_gauss_y, discrete_gauss_y, self.dx)
        rect_gauss_conv_x, rect_gauss_conv_y = self.signalGenerator.frequenceConvolution(discrete_rect_y, discrete_gauss_y, self.dx)
        PlotDrawer.drawPlotThirdLab(gauss_gauss_conv_x, gauss_gauss_conv_y, self.gaussXGaussPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка двух гауссовых сигналов")
        self.gaussXGaussPlotwidget.canvas.draw()
        PlotDrawer.drawPlotThirdLab(rect_gauss_conv_x, rect_gauss_conv_y, self.rectXGaussPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка прямоугольного и гауссова сигналов")
        self.rectXGaussPlotwidget.canvas.draw()
        
    def dxValueChangedHandler(self):
        self.dx = self.dxdoubleSpinBox.value()

        discrete_rect_x, discrete_rect_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        discrete_gauss_x, discrete_gauss_y=self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        rect_rect_conv_x, rect_rect_conv_y = self.signalGenerator.frequenceConvolution(discrete_rect_y, discrete_rect_y, self.dx)
        rect_gauss_conv_x, rect_gauss_conv_y = self.signalGenerator.frequenceConvolution(discrete_rect_y, discrete_gauss_y, self.dx)
        gauss_gauss_conv_x, gauss_gauss_conv_y = self.signalGenerator.frequenceConvolution(discrete_gauss_y, discrete_gauss_y, self.dx)
        PlotDrawer.drawPlotThirdLab(rect_rect_conv_x, rect_rect_conv_y, self.rectXRectPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка двух прямоугольных сигналов")
        self.rectXRectPlotwidget.canvas.draw()
        PlotDrawer.drawPlotThirdLab(rect_gauss_conv_x, rect_gauss_conv_y, self.rectXGaussPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка прямоугольного и гауссова сигналов")
        self.rectXGaussPlotwidget.canvas.draw()
        PlotDrawer.drawPlotThirdLab(gauss_gauss_conv_x, gauss_gauss_conv_y, self.gaussXGaussPlotwidget.figure, ['x', 'u1(x)*u2(x)'], "Свертка двух гауссовых сигналов")
        self.gaussXGaussPlotwidget.canvas.draw()
        
    def setupPlotWidget(self, container):
        figure = Figure()
        canvas = FigureCanvas(figure)

        if container.layout() is None:
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            layout = container.layout()
        layout.addWidget(canvas)

        container.canvas = canvas
        container.figure = figure
        ax = figure.add_subplot(111)
        ax.grid(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())