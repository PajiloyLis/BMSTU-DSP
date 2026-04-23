import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QVBoxLayout)
from PyQt6.uic import loadUi
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PIL import Image
import imageProcessor as ip

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('lab.ui', self)
        self.setupImageWidget(self.widget_input)
        self.setupImageWidget(self.widget_output)

        # Флаг для предотвращения рекурсии при автоматическом обновлении
        self._updating = False

        # Подключение сигналов кнопок
        self.pushButton_loadInput.clicked.connect(self.load_input_image)
        self.pushButton_saveOutput.clicked.connect(self.save_output_image)

        # Подключение сигналов для автоматического восстановления
        self.comboBox_distortion.currentTextChanged.connect(self.on_parameter_changed)
        self.checkBox_auto.toggled.connect(self.on_parameter_changed)
        self.spinBox_length.valueChanged.connect(self.on_parameter_changed)
        self.spinBox_angle.valueChanged.connect(self.on_parameter_changed)
        self.spinBox_radius.valueChanged.connect(self.on_parameter_changed)
        self.spinBox_K.valueChanged.connect(self.on_parameter_changed)

        # Инициализация состояния ручных полей
        self.toggle_manual_inputs()

        # Переменные для хранения данных
        self.input_image = None
        self.restored_image = None
        self.psf = None

    def on_parameter_changed(self):
        self.toggle_manual_inputs()
        """Вызывается при изменении любого параметра, влияющего на восстановление"""
        if not self._updating and self.input_image is not None:
            self.restore_image()

    def setupImageWidget(self, container):
        """Создаёт FigureCanvas для отображения изображения и встраивает в container"""
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
        ax.axis('off')
        return ax

    def toggle_manual_inputs(self):
        """Включает/выключает поля ручного ввода в зависимости от типа и режима"""
        auto = self.checkBox_auto.isChecked()
        distortion = self.comboBox_distortion.currentText()
        if distortion == "Смаз":
            self.spinBox_length.setEnabled(not auto)
            self.spinBox_angle.setEnabled(not auto)
            self.spinBox_radius.setEnabled(False)
        else:  # Дефокусировка
            self.spinBox_radius.setEnabled(not auto)
            self.spinBox_length.setEnabled(False)
            self.spinBox_angle.setEnabled(False)

    def load_input_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать искаженное изображение",
            "",
            "Изображения (*.bmp *.png *.jpg *.jpeg);;BMP (*.bmp);;PNG (*.png);;JPEG (*.jpg *.jpeg);;Все файлы (*)"
        )
        if file_path:
            self.lineEdit_inputPath.setText(file_path)
            try:
                img = Image.open(file_path).convert('L')
                self.input_image = np.array(img, dtype=np.float32) / 255.0
                ax = self.widget_input.figure.axes[0]
                ax.clear()
                ax.imshow(self.input_image, cmap='gray')
                ax.axis('off')
                self.widget_input.canvas.draw()
                # После загрузки запускаем восстановление
                self.restore_image()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение:\n{e}")

    def restore_image(self):
        if self.input_image is None:
            return

        self._updating = True
        try:
            distortion = self.comboBox_distortion.currentText()
            auto = self.checkBox_auto.isChecked()
            K = self.spinBox_K.value()

            # --- Оценка параметров PSF ---
            if distortion == "Смаз":
                if auto:
                    cep = ip.compute_cepstrum(self.input_image)
                    d, angle = ip.estimate_motion_blur_parameters(cep)
                    # Блокируем сигналы спинбоксов, чтобы не вызвать повторный пересчёт
                    self.spinBox_length.blockSignals(True)
                    self.spinBox_angle.blockSignals(True)
                    self.spinBox_length.setValue(d)
                    self.spinBox_angle.setValue(angle)
                    self.spinBox_length.blockSignals(False)
                    self.spinBox_angle.blockSignals(False)
                else:
                    d = self.spinBox_length.value()
                    angle = self.spinBox_angle.value()
                self.psf = ip.create_motion_blur_psf(self.input_image.shape, d, angle)
                if auto:
                    K = ip.estimate_wiener_k(self.psf)
                    self.spinBox_K.setValue(K)

            else:  # Дефокусировка
                if auto:
                    K = None
                    cep = ip.compute_cepstrum(self.input_image)
                    r = ip.estimate_defocus_radius(cep)
                    self.spinBox_radius.blockSignals(True)
                    self.spinBox_radius.setValue(r)
                    self.spinBox_radius.blockSignals(False)
                else:
                    r = self.spinBox_radius.value()
                self.psf = ip.create_defocus_psf(self.input_image.shape, r)
                if auto:
                    K = ip.estimate_wiener_k(self.psf)
                    self.spinBox_K.setValue(K)

            # --- Восстановление ---
            self.restored_image = ip.wiener_deconvolution(self.input_image, self.psf, K=K)
            # self.restore_image = ip.richardson_lucy_deconvolution(self.input_image, self.psf)
            restored = self.restored_image
            self.restored = (restored - np.min(restored)) / (np.max(restored) - np.min(restored))
            # --- Отображение результата ---
            ax = self.widget_output.figure.axes[0]
            ax.clear()
            ax.imshow(self.restored_image, cmap='gray')
            ax.axis('off')
            self.widget_output.canvas.draw()

        except Exception as e:
            # Не показываем сообщение при каждом изменении параметра, можно выводить в статусбар
            print(f"Ошибка восстановления: {e}")
        finally:
            self._updating = False

    def save_output_image(self):
        if self.restored_image is None:
            QMessageBox.warning(self, "Предупреждение", "Нет восстановленного изображения для сохранения.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить восстановленное изображение", "", "Изображения (*.bmp *.png *.jpg *.jpeg);;BMP (*.bmp);;PNG (*.png);;JPEG (*.jpg *.jpeg);;Все файлы (*)")
        if file_path:
            try:
                # Масштабируем обратно в 0..255 и сохраняем
                img_out = (self.restored_image * 255).astype(np.uint8)
                Image.fromarray(img_out).save(file_path)
                self.lineEdit_outputPath.setText(file_path)
                QMessageBox.information(self, "Успех", f"Изображение сохранено:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())