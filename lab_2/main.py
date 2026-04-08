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
        self.setupPlotWidget(self.gaussPlotwidget)
        self.setupPlotWidget(self.rectPlotwidget)
        self.rectLdoubleSpinBox.valueChanged.connect(self.rectLValueCangedHandler)
        self.dxdoubleSpinBox.valueChanged.connect(self.dxValueChangedHandler)
        self.gaussSigmadoubleSpinBox.valueChanged.connect(self.gaussSigmaValueChangedHandler)

    def rectLValueCangedHandler(self):
        self.l = self.rectLdoubleSpinBox.value()
        # signal_x, signal_y = self.signalGenerator.generateRect(self.l)
        discrete_x, discret_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        shifted_discret_y = SignalGenerator.removeTwinsTransform(discrete_x, discret_y)
        dft_x, dft_y, dft_time = SignalGenerator.dft(shifted_discret_y, self.dx)
        fft_x, fft_y, fft_time = SignalGenerator.fft(shifted_discret_y, self.dx)
        PlotDrawer.drawPlotsSecondLab((dft_x, fft_x), (dft_y, fft_y), 
                                     self.rectPlotwidget.figure, ("DFT", "FFT"), 
                                     ("f", "V(f)"), "Преобразование Фурье прямоугольного сигнала")
        self.rectPlotwidget.canvas.draw()
        self.RectTimeFFTLabel.setText(str(fft_time))
        self.RectTimeDFTLabel.setText(str(dft_time))
    
    def gaussSigmaValueChangedHandler(self):
        self.sigma = self.gaussSigmadoubleSpinBox.value()
        # signal_x, signal_y = self.signalGenerator.generateGauss(self.sigma)
        discrete_x, discret_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        shifted_discret_y = SignalGenerator.removeTwinsTransform(discrete_x, discret_y)
        dft_x, dft_y, dft_time = SignalGenerator.dft(shifted_discret_y, self.dx)
        fft_x, fft_y , fft_time = SignalGenerator.fft(shifted_discret_y, self.dx)
        PlotDrawer.drawPlotsSecondLab((dft_x, fft_x), (dft_y, fft_y), 
                                     self.gaussPlotwidget.figure, ("DFT", "FFT"), 
                                     ("f", "V(f)"), "Преобразование Фурье гауссова сигнала")
        self.gaussPlotwidget.canvas.draw()
        self.GaussTimeFFTLabel.setText(str(fft_time))
        self.GaussTimeDFTLabel.setText(str(dft_time))

    def dxValueChangedHandler(self):
        self.dx = self.dxdoubleSpinBox.value()

        discrete_x, discret_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        shifted_discret_y = SignalGenerator.removeTwinsTransform(discrete_x, discret_y)
        dft_x, dft_y, dft_time = SignalGenerator.dft(shifted_discret_y, self.dx)
        fft_x, fft_y , fft_time = SignalGenerator.fft(shifted_discret_y, self.dx)
        PlotDrawer.drawPlotsSecondLab((dft_x, fft_x), (dft_y, fft_y), 
                                     self.gaussPlotwidget.figure, ("DFT", "FFT"), 
                                     ("f", "V(f)"), "Преобразование Фурье гауссова сигнала")
        self.gaussPlotwidget.canvas.draw()
        self.GaussTimeFFTLabel.setText(str(fft_time))
        self.GaussTimeDFTLabel.setText(str(dft_time))

        discrete_x, discret_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        shifted_discret_y = SignalGenerator.removeTwinsTransform(discrete_x, discret_y)
        dft_x, dft_y, dft_time = SignalGenerator.dft(shifted_discret_y, self.dx)
        fft_x, fft_y, fft_time = SignalGenerator.fft(shifted_discret_y, self.dx)
        PlotDrawer.drawPlotsSecondLab((dft_x, fft_x), (dft_y, fft_y), 
                                     self.rectPlotwidget.figure, ("DFT", "FFT"), 
                                     ("f", "V(f)"), "Преобразование Фурье прямоугольного сигнала")
        self.rectPlotwidget.canvas.draw()
        self.RectTimeFFTLabel.setText(str(fft_time))
        self.RectTimeDFTLabel.setText(str(dft_time))

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