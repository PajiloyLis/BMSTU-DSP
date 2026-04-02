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
        # Загружаем .ui файл и применяем к текущему окну
        loadUi('alb.ui', self)
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
        signal_x, signal_y = self.signalGenerator.generateRect(self.l)
        discret_x, discret_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        recovered_y = self.signalGenerator.generateReconstructed(discret_x, discret_y, signal_x, self.dx)
        PlotDrawer.drawPlotsFirstLab((signal_x, discret_x, signal_x), (signal_y, discret_y, recovered_y), 
                                     self.rectPlotwidget.figure, ("Исходный", "Дискретный", "Восстановленный"), 
                                     ("x", "U(x)"), "Прямоугольный сигнал")
        self.rectPlotwidget.canvas.draw()
    
    def gaussSigmaValueChangedHandler(self):
        self.sigma = self.gaussSigmadoubleSpinBox.value()
        signal_x, signal_y = self.signalGenerator.generateGauss(self.sigma)
        discret_x, discret_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        recovered_y = self.signalGenerator.generateReconstructed(discret_x, discret_y, signal_x, self.dx)
        PlotDrawer.drawPlotsFirstLab((signal_x, discret_x, signal_x), (signal_y, discret_y, recovered_y), 
                                     self.gaussPlotwidget.figure, ("Исходный", "Дискретный", "Восстановленный"), 
                                     ("x", "U(x)"), "Гауссов сигнал")
        self.gaussPlotwidget.canvas.draw()

    def dxValueChangedHandler(self):
        self.dx = self.dxdoubleSpinBox.value()

        signal_x, signal_y = self.signalGenerator.generateGauss(self.sigma)
        discret_x, discret_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        recovered_y = self.signalGenerator.generateReconstructed(discret_x, discret_y, signal_x, self.dx)
        PlotDrawer.drawPlotsFirstLab((signal_x, discret_x, signal_x), (signal_y, discret_y, recovered_y), 
                                     self.gaussPlotwidget.figure, ("Исходный", "Дискретный", "Восстановленный"), 
                                     ("x", "U(x)"), "Гауссов сигнал")
        self.gaussPlotwidget.canvas.draw()

        signal_x, signal_y = self.signalGenerator.generateRect(self.l)
        discret_x, discret_y = self.signalGenerator.generateDiscretRect(self.l, self.dx)
        recovered_y = self.signalGenerator.generateReconstructed(discret_x, discret_y, signal_x, self.dx)
        PlotDrawer.drawPlotsFirstLab((signal_x, discret_x, signal_x), (signal_y, discret_y, recovered_y), 
                                     self.rectPlotwidget.figure, ("Исходный", "Дискретный", "Восстановленный"), 
                                     ("x", "U(x)"), "Прямоугольный сигнал")
        self.rectPlotwidget.canvas.draw()

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