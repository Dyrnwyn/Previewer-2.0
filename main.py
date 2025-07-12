from sys import argv
from os.path import split as path_split, join as path_join
from lib.static_method import show_message_box
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QApplication, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QObject
from PIL.ImageQt import ImageQt
from previewer2_main_window import Ui_MainWindow
from previewer2_logick import Previewer
from lib.psd_convert import PSDWorker
from lib.settings import PreviewerSettings
from lib.static_method import get_layers_name_from_psd


class MainApp(QMainWindow, Ui_MainWindow, QObject):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.settings = PreviewerSettings()
        self.set_settings_on_form()

        self.error_plainTextEdit.setVisible(False)
        self.error_plainTextEdit.setEnabled(True)

        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.label_what_in_work.setVisible(False)

        self.checkBox_holst.clicked.connect(self.holst_check_choice)
        self.checkBox_with_price.clicked.connect(self.price_check_choice)

        self.toolButton_choice_path.clicked.connect(self.set_path_and_object_name)
        self.toolButton_select_psd_file.clicked.connect(self.select_psd)
        self.pushButton_compose.clicked.connect(self.compose_preview)

        self.pushButton_remove_file_settings.clicked.connect(self.set_default_settings)
        self.pushButton_change_layer_in_files.clicked.connect(self.replace_layer)
        self.toolButton_pickup_dir.clicked.connect(self.pickup_convertation_dir)
        self.pushButton_convert_psd.clicked.connect(self.convert_psd_to_jpeg)

        self.pushButton_save_settings.clicked.connect(self.save_settings)
        self.toolButton_RegularFont.clicked.connect(self.tool_button_regular_select_file)
        self.toolButton_BoldFont.clicked.connect(self.tool_button_bold_select_file)
        self.toolButton_ItalicFont.clicked.connect(self.tool_button_italic_select_file)

        self.comboBox_layers.currentIndexChanged.connect(self.output_image)

    def set_default_settings(self) -> None:
        self.settings.set_default_settings()
        self.set_settings_on_form()

    def on_change_what_in_work(self, msg):
        self.label_what_in_work.setText(msg)

    def on_change_set_value_pg(self, v):
        self.progressBar.setValue(v)

    def on_change_maximum_pg(self, v):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(v)

    def on_change_missed_files(self, msg):
        if not self.error_plainTextEdit.isVisible():
            self.error_plainTextEdit.setVisible(True)
        self.error_plainTextEdit.insertPlainText(msg)

    def on_start_previewer(self):
        self.error_plainTextEdit.setPlainText("")
        self.error_plainTextEdit.setVisible(False)
        self.progressBar.setVisible(True)
        self.label_what_in_work.setVisible(True)
        self.lineEdit_path.setEnabled(False)
        self.lineEdit_object_name.setEnabled(False)
        self.pushButton_compose.setEnabled(False)
        self.checkBox_holst.setEnabled(False)
        self.checkBox_with_price.setEnabled(False)

        self.lineEdit_path_to_psd.setEnabled(False)
        self.lineEdit_psd_file.setEnabled(False)
        self.toolButton_select_psd_file.setEnabled(False)
        self.toolButton_pickup_dir.setEnabled(False)
        self.pushButton_change_layer_in_files.setEnabled(False)
        self.pushButton_convert_psd.setEnabled(False)

    def on_finish_previewer(self):
        self.set_form_after_compose_previewer()

    @staticmethod
    def msg_compose_result(dict_result):
        show_message_box(dict_result["title_text"], dict_result["msg"])

    def set_form_after_compose_previewer(self):
        self.lineEdit_path.setEnabled(True)
        self.lineEdit_object_name.setEnabled(True)
        self.pushButton_compose.setEnabled(True)
        self.checkBox_holst.setEnabled(True)
        self.checkBox_with_price.setEnabled(True)
        self.progressBar.setVisible(False)
        self.label_what_in_work.setVisible(False)

        self.lineEdit_path_to_psd.setEnabled(True)
        self.lineEdit_psd_file.setEnabled(True)
        self.toolButton_select_psd_file.setEnabled(True)
        self.toolButton_pickup_dir.setEnabled(True)
        self.pushButton_change_layer_in_files.setEnabled(True)
        self.pushButton_convert_psd.setEnabled(True)

    def compose_preview(self):
        previewer_thread = Previewer(self, self.settings, self.lineEdit_object_name.text(), self.lineEdit_path.text())
        previewer_thread.started.connect(self.on_start_previewer)
        previewer_thread.finished.connect(self.on_finish_previewer)
        previewer_thread.compose_result.connect(self.msg_compose_result)
        previewer_thread.what_in_work.connect(self.on_change_what_in_work)
        previewer_thread.progress_bar_percent.connect(self.on_change_set_value_pg)
        previewer_thread.progress_bar_maximum.connect(self.on_change_maximum_pg)
        previewer_thread.missed_files.connect(self.on_change_missed_files)
        previewer_thread.start()

    def psd_worker(self, convert=False, replace_layer=False):
        converter_thread = PSDWorker(self, self.lineEdit_path_to_psd.text(), self.lineEdit_psd_file.text(),
                                     convert, replace_layer,
                                     self.comboBox_layers.itemData(self.comboBox_layers.currentIndex()),
                                     self.comboBox_layers.itemData(self.comboBox_layers.currentIndex() - 1))
        converter_thread.started.connect(self.on_start_previewer)
        converter_thread.finished.connect(self.on_finish_previewer)
        converter_thread.compose_result.connect(self.msg_compose_result)
        converter_thread.what_in_work.connect(self.on_change_what_in_work)
        converter_thread.progress_bar_percent.connect(self.on_change_set_value_pg)
        converter_thread.progress_bar_maximum.connect(self.on_change_maximum_pg)
        converter_thread.missed_files.connect(self.on_change_missed_files)
        converter_thread.start()

    def convert_psd_to_jpeg(self):
        if not self.lineEdit_path_to_psd.text() == "":
            self.psd_worker(True)

    def replace_layer(self):
        if (not self.lineEdit_path_to_psd.text() == "") and \
                (not self.lineEdit_psd_file.text() == ""):
            self.psd_worker(False, True)

    def get_settings_from_form(self):
        self.settings.species = self.spinBox_species.value()
        self.settings.format = self.spinBox_format.value()
        self.settings.template = self.spinBox_template.value()
        self.settings.photo = self.spinBox_photo.value()
        self.settings.number = self.spinBox_number.value()
        self.settings.school_class = self.spinBox_class.value()
        self.settings.id = self.spinBox_id.value()
        self.settings.summ = self.spinBox_summ.value()
        self.settings.text_for_qr = self.textEdit_qr_text.toPlainText()
        self.settings.qr_error_correct['index'] = self.comboBox_error_correction_level.currentIndex()
        self.settings.qr_error_correct['text'] = self.comboBox_error_correction_level.currentText()
        self.settings.font_regular = self.lineEdit_RegularFont.text()
        self.settings.font_bold = self.lineEdit_BoldFont.text()
        self.settings.font_italic = self.lineEdit_ItalicFont.text()
        self.settings.bottom_text = self.textEdit_bottom_text.toPlainText()

    def set_settings_on_form(self):
        self.spinBox_species.setValue(self.settings.species)
        self.spinBox_format.setValue(self.settings.format)
        self.spinBox_template.setValue(self.settings.template)
        self.spinBox_photo.setValue(self.settings.photo)
        self.spinBox_number.setValue(self.settings.number)
        self.spinBox_class.setValue(self.settings.school_class)
        self.spinBox_id.setValue(self.settings.id)
        self.spinBox_summ.setValue(self.settings.summ)
        self.textEdit_qr_text.setText(self.settings.text_for_qr)
        self.comboBox_error_correction_level.setCurrentIndex(self.settings.qr_error_correct['index'])
        self.lineEdit_RegularFont.setText(self.settings.font_regular)
        self.lineEdit_BoldFont.setText(self.settings.font_bold)
        self.lineEdit_ItalicFont.setText(self.settings.font_italic)
        self.textEdit_bottom_text.setText(self.settings.bottom_text)

    def save_settings(self):
        self.get_settings_from_form()
        self.settings.save_settings()

    def select_psd(self):
        selected_file = QFileDialog.getOpenFileName(self.window(), caption="Выберите psd файл",
                                                    filter='Adobe Photoshop(psd) (*.psd)',
                                                    initialFilter='Adobe Photoshop(psd) (*.psd)')
        if not selected_file[0] == '':
            head, tail = path_split(selected_file[0])
            self.lineEdit_psd_file.setText(tail)
            if self.lineEdit_path_to_psd.text() == '':
                self.lineEdit_path_to_psd.setText(head)
            self.get_layers(head, tail)

    def get_layers(self, work_path, filename):
        layer_list = get_layers_name_from_psd(path_join(work_path, filename))
        self.comboBox_layers.clear()
        for layer in layer_list:
            self.comboBox_layers.addItem(list(layer.keys())[0], userData=list(layer.values())[0])
        self.output_image()

    def pickup_convertation_dir(self):
        path_text = QFileDialog.getExistingDirectory()
        self.lineEdit_path_to_psd.setText(path_text)

    def tool_button_regular_select_file(self):
        self.select_file(self.lineEdit_RegularFont, "Выберите файл шрифта 'Regular'")

    def tool_button_bold_select_file(self):
        self.select_file(self.lineEdit_BoldFont, "Выберите файл шрифта 'Bold'")

    def tool_button_italic_select_file(self):
        self.select_file(self.lineEdit_ItalicFont, "Выберите файл шрифта 'Italic'")

    def select_file(self, line_edit, caption_text="Выберите файл шрифта"):
        selected_file = QFileDialog.getOpenFileName(self.window(), caption=caption_text,
                                                    filter='Fonts(ttf) (*.ttf)',
                                                    initialFilter='Fonts(ttf) (*.ttf)')
        if not selected_file[0] == '':
            line_edit.setText(selected_file[0])

    def set_path_and_object_name(self):
        path_text = QFileDialog.getExistingDirectory()
        self.lineEdit_path.setText(path_text)
        self.lineEdit_object_name.setText(path_text.split("/")[-1])

    def price_check_choice(self):
        if self.checkBox_with_price.isChecked():
            self.checkBox_holst.setCheckState(Qt.CheckState.Unchecked)
            self.settings.with_price = True
        else:
            self.settings.with_price = False

    def holst_check_choice(self):
        if self.checkBox_holst.isChecked():
            self.checkBox_with_price.setCheckState(Qt.CheckState.Unchecked)
            self.settings.holst = True
        else:
            self.settings.holst = False

    def output_image(self):
        scene = QGraphicsScene(0, 0, 400, 150)
        layer = self.comboBox_layers.itemData(self.comboBox_layers.currentIndex())
        if layer is not None:
            layer.visible = True
            qt_image = ImageQt(layer.composite().resize([300,150]))
            scene.addItem(QGraphicsPixmapItem(QPixmap(QImage(qt_image))))
            self.graphicsView_view_layer.setScene(scene)

def main():
    app = QApplication(argv)
    main_window = MainApp()
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()
