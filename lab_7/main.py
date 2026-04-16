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
        self.sigma_f_input = self.Sigma_F_Input_doubleSpinBox.value()
        self.sigma_output = self.gaussSigmaOutputdoubleSpinBox.value()
        self.sigma_f_output = self.Sigma_F_Output_doubleSpinBox.value()
        self.signalGenerator = SignalGenerator(-5., 5.)
        self.setupPlotWidget(self.Weiner_widget)
        self.dxdoubleSpinBox.valueChanged.connect(self.dxValueChangedHandler)
        self.gaussSigmaInputdoubleSpinBox.valueChanged.connect(self.gaussSigmaInputValueChangedHandler)
        self.Sigma_F_Input_doubleSpinBox.valueChanged.connect(self.SigmaFValueChangedHandler)
        self.gaussSigmaOutputdoubleSpinBox.valueChanged.connect(self.gaussSigmaInputValueChangedHandler)
        self.Sigma_F_Output_doubleSpinBox.valueChanged.connect(self.SigmaFValueChangedHandler)
        
    def gaussSigmaInputValueChangedHandler(self):
        self.sigma = self.gaussSigmadoubleSpinBox.value()
        
        ideal_x, ideal_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        
        if self.noiseType == NoiseType.GAUSS:
            noise_y = SignalGenerator.generateGaussNoise(ideal_y, self.dx, self.sigma_f)
        else:
            noise_y = SignalGenerator.generateImpulseNoise(ideal_y)
            
        result_y = SignalGenerator.applyNoise(ideal_y, noise_y)
        
        filtered_y = SignalGenerator.applyWeiner(result_y, self.dx, noise_y)
        
        PlotDrawer.drawPlotFourthLab((ideal_x, ideal_x, ideal_x), (ideal_y, result_y, filtered_y), self.Weiner_widget.figure, ("Полезный сигнал", "Результирующий сигнал", "Фильтрованный сигнал"), ("x", "u(x)"), "Фильтр Винера")
        
        self.Weiner_widget.canvas.draw()
        
    def dxValueChangedHandler(self):
        self.dx = self.dxdoubleSpinBox.value()
        
        ideal_x, ideal_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        
        if self.noiseType == NoiseType.GAUSS:
            noise_y = SignalGenerator.generateGaussNoise(ideal_y, self.dx, self.sigma_f)
        else:
            noise_y = SignalGenerator.generateImpulseNoise(ideal_y)
            
        result_y = SignalGenerator.applyNoise(ideal_y, noise_y)
        
        filtered_y = SignalGenerator.applyWeiner(result_y, self.dx, noise_y)
        
        PlotDrawer.drawPlotFourthLab((ideal_x, ideal_x, ideal_x), (ideal_y, result_y, filtered_y), self.Weiner_widget.figure, ("Полезный сигнал", "Результирующий сигнал", "Фильтрованный сигнал"), ("x", "u(x)"), "Фильтр Винера")
        
        self.Weiner_widget.canvas.draw()
        
    def SigmaFValueChangedHandler(self):
        self.sigma_f = self.Sigma_F_doubleSpinBox.value()
        
        ideal_x, ideal_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        
        noise_y = SignalGenerator.generateGaussNoise(ideal_y, self.dx, self.sigma_f)
            
        result_y = SignalGenerator.applyNoise(ideal_y, noise_y)
        
        filtered_y = SignalGenerator.applyWeiner(result_y, self.dx, noise_y)
        
        PlotDrawer.drawPlotFourthLab((ideal_x, ideal_x, ideal_x), (ideal_y, result_y, filtered_y), self.Weiner_widget.figure, ("Полезный сигнал", "Результирующий сигнал", "Фильтрованный сигнал"), ("x", "u(x)"), "Фильтр Винера")
        
        self.Weiner_widget.canvas.draw()
        
    def GaussNoiseSelected(self):
        self.Sigma_F_doubleSpinBox.setEnabled(True)
        self.noiseType = NoiseType.GAUSS
        
        ideal_x, ideal_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        
        noise_y = SignalGenerator.generateGaussNoise(ideal_y, self.dx, self.sigma_f)
            
        result_y = SignalGenerator.applyNoise(ideal_y, noise_y)
        
        filtered_y = SignalGenerator.applyWeiner(result_y, self.dx, noise_y)
        
        PlotDrawer.drawPlotFourthLab((ideal_x, ideal_x, ideal_x), (ideal_y, result_y, filtered_y), self.Weiner_widget.figure, ("Полезный сигнал", "Результирующий сигнал", "Фильтрованный сигнал"), ("x", "u(x)"), "Фильтр Винера")
        
        self.Weiner_widget.canvas.draw()
        
    def ImpulseNoiseSelected(self):
        self.Sigma_F_doubleSpinBox.setEnabled(False)
        self.noiseType=NoiseType.IMPULSE
        
        ideal_x, ideal_y = self.signalGenerator.generateDiscretGauss(self.sigma, self.dx)
        
        noise_y = SignalGenerator.generateImpulseNoise(ideal_y)
            
        result_y = SignalGenerator.applyNoise(ideal_y, noise_y)
        
        filtered_y = SignalGenerator.applyWeiner(result_y, self.dx, noise_y)
        
        PlotDrawer.drawPlotFourthLab((ideal_x, ideal_x, ideal_x), (ideal_y, result_y, filtered_y), self.Weiner_widget.figure, ("Полезный сигнал", "Результирующий сигнал", "Фильтрованный сигнал"), ("x", "u(x)"), "Фильтр Винера")
        
        self.Weiner_widget.canvas.draw()
        
    def Processing(self):
        ideal_input_x, ideal_input_y = self.signalGenerator.generateDiscretGauss(self.sigma_f_input, self.dx)
        noise_input_y = SignalGenerator.generateImpulseNoise(ideal_input_y, np.random.uniform(0.05, 0.1))
        result_input_y = SignalGenerator.applyNoise(ideal_input_y, noise_input_y)
        
        ideal_output_x, ideal_output_y = self.signalGenerator.generateDiscretGauss(self.sigma_f_output, self.dx)
        noise_output_y = SignalGenerator.generateImpulseNoise(ideal_output_y, np.random.uniform(0.05, 0.1))
        result_output_y = SignalGenerator.applyNoise(ideal_output_y, noise_output_y)
        
        
        
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