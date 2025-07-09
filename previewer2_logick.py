import logging
from os import remove
from os.path import join as joint_path, exists as path_exist

from PIL.Image import open as open_image
from PyQt6.QtCore import QThread, pyqtSignal
from psd_tools import PSDImage

from lib import draw_page
from lib.holst import get_prepared_files_for_holst_preview
from lib.static_method import get_file_sizes, get_list_of_psd_files, get_list_of_pdf_files, \
    get_parametrs_from_file_name


class Previewer(QThread):
    what_in_work = pyqtSignal(str)
    missed_files = pyqtSignal(str)
    progress_bar_percent = pyqtSignal(int)
    progress_bar_maximum = pyqtSignal(int)
    compose_result = pyqtSignal(dict)
    logging.basicConfig(filename='previewer.log', filemode='w', format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.INFO)

    def __init__(self, parent, settings, object_name, object_path):
        super().__init__(parent=parent)
        self.object_name = object_name
        self.object_path = object_path
        self.psd_files = []
        # self.holst_files = []
        self.settings = settings
        self.files_for_preview = {}
        self.dict_of_class = {"Класс": [], }
        self.missed_files_msg = "Ошибка при обработке: {0}\n"

    def run(self):
        if not self.check_data_to_compose_preview():
            return
        self.remove_old_pdf()
        self.compose_preview()
        self.compose_result.emit(self.get_compose_result("Завершение формирования",
                                                         "Превью успешно сформировано"))

    def stop_thread(self, title_text, msg):
        self.compose_result.emit(self.get_compose_result(title_text, msg))
        self.quit()


    def compose_preview(self):
        if self.settings.holst:
            holst_files = get_prepared_files_for_holst_preview(self.object_path, self.settings.holst_files_subdir)
            self.convert_jpg(holst_files)
        else:
            self.psd_files = get_list_of_psd_files(self.object_path)
            self.convert_psd()
        self.create_dict_of_class()
        self.sort_dictionary()
        self.generate_pdf()

    @staticmethod
    def get_compose_result(title_text, msg):
        result_dict = {"title_text": title_text, "msg": msg}
        return result_dict

    def check_data_to_compose_preview(self):
        if not self.object_path:
            self.stop_thread("Ошибка", "Не выбрана папка с объектом")
            return False
        if not self.object_name:
            self.stop_thread("Ошибка", "Необходимо указать имя объект")
            return False
        if not self.check_font():
            return False
        return True

    def convert_psd(self, resize=True):
        self.initialize_progress_bar(len(self.psd_files))
        count = 0
        for psd_file_name in self.psd_files:
            abs_path = joint_path(self.object_path, psd_file_name)
            img_file = self.open_image_file(psd_file_name, abs_path, True)
            if img_file is None:
                continue
            if resize:
                width, height = get_file_sizes(img_file)
                img_file = img_file.resize((width, height))
            self.add_file_to_files_for_preview(psd_file_name, img_file)
            count += 1
            self.set_new_value_of_progress_bar(count)

    def add_file_to_files_for_preview(self, psd_file_name, img_file):
        self.files_for_preview['{0}{1}'.format(psd_file_name[0:-4], ".jpeg")] = img_file

    def convert_jpg(self, holst_files):
        self.initialize_progress_bar(len(holst_files))
        count = 0
        for jpg_file_name in holst_files:
            abs_path = joint_path(self.object_path, self.settings.holst_files_subdir, jpg_file_name)
            img_file = self.open_image_file(jpg_file_name, abs_path)
            if img_file is None:
                continue
            width, height = get_file_sizes(img_file)
            self.files_for_preview[jpg_file_name[0:-4] + ".jpeg"] = img_file.resize((width, height))
            count += 1
            self.set_new_value_of_progress_bar(count)

    def open_image_file(self, img_file_name, abs_path, is_psd=False):
        log_message = "Обрабатываю файл: {0}".format(img_file_name)
        self.set_what_in_work(log_message)
        logging.info(log_message)
        if path_exist(abs_path):
            try:
                if is_psd:
                    psd = PSDImage.open(abs_path)
                else:
                    img = open_image(abs_path)
                    return img
            except Exception:
                self.output_error("Не удалось открыть файл: {0}".format(img_file_name))
                return None
        else:
            self.output_error("Не удалось найти файл: {0}".format(img_file_name))
            return None
        try:
            self.set_what_in_work("Конвертирую файл: {0}".format(img_file_name))
            rgb_png = psd.composite().convert("RGB")
            return rgb_png
        except Exception as E:
            self.output_error("Не удалось конвертировать: {0}".format(img_file_name))
            return None

    def set_new_value_of_progress_bar(self, new_value):
        self.progress_bar_percent.emit(new_value)

    def initialize_progress_bar(self, max_pb):
        self.progress_bar_maximum.emit(max_pb)
        self.progress_bar_percent.emit(0)

    def set_what_in_work(self, message):
        self.what_in_work.emit(message)

    def output_error(self, message):
        logging.error(message)
        self.missed_files.emit(message)

    def sort_dictionary(self):
        logging.info("Сортирую полученные классы.")
        tmp_list = []
        class_list_sorted = {}
        for key, val in self.dict_of_class.items():
            tmp_list.append(key)
        tmp_list_sorted = sorted(tmp_list)
        for key in tmp_list_sorted:
            class_list_sorted[key] = []
            class_list_sorted[key] = self.dict_of_class[key]
        self.dict_of_class = class_list_sorted

    def create_dict_of_class(self):
        # функция создания словаря с "классами", если "класс""
        # в файле не указан, файл будет добавлен в "Класс" по умолчанию
        logging.info("Получаю классы из файлов.")
        for file_name in self.files_for_preview.keys():
            i = file_name.split("_")
            if i[5] not in self.dict_of_class.keys():
                self.dict_of_class[i[5]] = []
                logging.info("Найден класс: {0}".format(i[5]))
                self.dict_of_class[i[5]].append({file_name: self.files_for_preview[file_name]})
            else:
                self.dict_of_class[i[5]].append({file_name: self.files_for_preview[file_name]})

    def generate_pdf(self):
        self.initialize_progress_bar(len(self.files_for_preview))
        count_for_pb = 0
        page = None
        for key, val in self.dict_of_class.items():
            cell = 0
            count = 0
            for item in val:
                for file_name, image in item.items():
                    self.what_in_work.emit("Добавляю в превью: Класс {0} ({1})".format(key, file_name))
                    cell += 1
                    count += 1
                    if cell == 1:
                        page = draw_page.Page(self.settings.font_regular,
                                              self.settings.font_bold,
                                              self.settings.font_italic)

                        page.draw_name_object(self.object_name)
                        page.draw_of_klass(key)
                    photo_parametrs = get_parametrs_from_file_name(file_name)
                    if self.settings.with_price:
                        if photo_parametrs['id_client'] == "":
                            self.output_error((self.missed_files_msg + ": не указан ID клиента\n").format(file_name))
                        if photo_parametrs['cost'] == "":
                            self.output_error((self.missed_files_msg + ": не указана стоимость изделия\n").format(file_name))
                    page.draw_information_of_photo(cell, photo_parametrs, self.settings, image)
                    count_for_pb += 1
                    self.progress_bar_percent.emit(count_for_pb)
                    if cell == 4 or count == len(val):
                        page.save_page(self.object_name, self.object_path)
                        # page.__init__()
                        cell = 0

    def remove_old_pdf(self):
        self.set_what_in_work("Удаляю старое превью")
        pdf_files = get_list_of_pdf_files(self.object_path)
        pdf_file_name = self.object_name + ".pdf"
        if pdf_file_name in pdf_files:
            full_filename = joint_path(self.object_path, pdf_file_name)
            logging.info("Удаление старого превью: {0}".format(full_filename))
            remove(full_filename)

    def check_font(self):
        fonts = [self.settings.font_regular, self.settings.font_bold, self.settings.font_italic]
        for font in fonts:
            if not path_exist(font):
                self.stop_thread("Ошибка", "Не удалось обнаружить шрифт по указанному пути: {0}".format(font))
                return False
        return True
