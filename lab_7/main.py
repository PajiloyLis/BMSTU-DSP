import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt6.uic import loadUi
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from signalGenerator import SignalGenerator, NoiseType, FrequencyType
from plotDrawer import PlotDrawer
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('lab.ui', self)
        self.dx = self.dxdoubleSpinBox.value()
        self.sigma_input = self.gaussSigmaInputdoubleSpinBox.value()
        self.delta = self.Sigma_F_Input_doubleSpinBox.value()
        self.sigma_output = self.gaussSigmaOutputdoubleSpinBox.value()
        self.eps = self.Sigma_F_Output_doubleSpinBox.value()
        self.signalGenerator = SignalGenerator(-5., 5.)
        self.setupPlotWidget(self.Weiner_widget)
        self.dxdoubleSpinBox.valueChanged.connect(self.dxValueChangedHandler)
        self.gaussSigmaInputdoubleSpinBox.valueChanged.connect(self.gaussSigmaInputValueChangedHandler)
        self.Sigma_F_Input_doubleSpinBox.valueChanged.connect(self.SigmaFInputValueChangedHandler)
        self.gaussSigmaOutputdoubleSpinBox.valueChanged.connect(self.gaussSigmaOutputValueChangedHandler)
        self.Sigma_F_Output_doubleSpinBox.valueChanged.connect(self.SigmaFOutputValueChangedHandler)
        
        
    def dxValueChangedHandler(self):
        self.dx = self.dxdoubleSpinBox.value()
        
        self.Processing()
        
    def gaussSigmaInputValueChangedHandler(self):
        self.sigma_input = self.gaussSigmaInputdoubleSpinBox.value()
        self.Processing()
        
    def SigmaFInputValueChangedHandler(self):
        self.delta = self.Sigma_F_Input_doubleSpinBox.value()
        self.Processing()
        
    def gaussSigmaOutputValueChangedHandler(self):
        self.sigma_output = self.gaussSigmaOutputdoubleSpinBox.value()
        self.Processing()
        
    def SigmaFOutputValueChangedHandler(self):
        self.eps = self.Sigma_F_Output_doubleSpinBox.value()
        self.Processing()
        

    def Processing(self):
        ideal_input_x, ideal_input_y = self.signalGenerator.generateDiscretGauss(self.sigma_input, self.dx)
        noise_input_y = SignalGenerator.generateImpulseNoise(ideal_input_y, self.delta)
        result_input_y_real = SignalGenerator.applyNoise(ideal_input_y, noise_input_y)
        result_input_y = SignalGenerator.removeTwinsTransform(ideal_input_x, result_input_y_real)
        
        ideal_output_x, ideal_output_y = self.signalGenerator.generateDiscretGauss(self.sigma_output, self.dx)
        noise_output_y = SignalGenerator.generateImpulseNoise(ideal_output_y, self.eps)
        result_output_y_real = SignalGenerator.applyNoise(ideal_output_y, noise_output_y)
        result_output_y = SignalGenerator.removeTwinsTransform(ideal_output_x, result_output_y_real)
        
        alpha = self.signalGenerator.compute_alpha(result_input_y, result_output_y, self.dx, self.delta, self.eps)
        h_x, h, _ = self.signalGenerator.regularizationTikhonov(result_input_y, result_output_y, self.dx, alpha)
        
        PlotDrawer.drawPlotFourthLab((ideal_input_x, ideal_output_x, h_x), (result_input_y_real, result_output_y_real, h), self.Weiner_widget.figure, ("Входной сигнал", "Выходной сигнал", "Функция импульсного отклика"), ("x", "u(x)"), "Регуляризация Тихонова")
        
        self.Weiner_widget.canvas.draw()
        
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