import logging
import draw_page
from static_method import get_file_sizes, search_file_with_extension
from PyQt5.QtCore import QThread, pyqtSignal
from os import path, remove, sep
from psd_tools import PSDImage
from PIL.Image import BICUBIC
from PIL import Image


class Previewer(QThread):
    settings = {}
    files_for_preview = {}
    dict_of_class = {"Класс": [], }
    what_in_work = pyqtSignal(str)
    missed_files = pyqtSignal(str)
    missed_files_msg = "Ошибка при обработке: {0}\n"
    progress_bar_percent = pyqtSignal(int)
    progress_bar_maximum = pyqtSignal(int)
    logging.basicConfig(filename='previewer.log', filemode='w', format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.INFO)

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.remove_old_pdf()
        if self.settings['holst']:
            self.convert_jpg()
        else:
            self.convert_psd()
        self.create_dict_of_class()
        self.sort_dictionary()
        self.generate_pdf()

    def set_var(self, settings):
        self.settings = settings

    def convert_psd(self):
        self.initialize_progress_bar(len(self.settings['psd_files']))
        count = 0
        for psd_file_name in self.settings['psd_files']:
            abs_path = path.join(self.settings['path'], psd_file_name)
            img_file = self.open_image_file(psd_file_name, abs_path, True)
            if img_file is None:
                continue
            width, height = get_file_sizes(img_file)
            self.files_for_preview[psd_file_name[0:-4] + ".jpeg"] = img_file.resize((width, height), BICUBIC)
            count += 1
            self.set_new_value_of_progress_bar(count)

    def convert_jpg(self):
        self.initialize_progress_bar(len(self.settings['holst_files']))
        count = 0
        for jpg_file_name in self.settings['holst_files']:
            abs_path = path.join(self.settings['path'], self.settings['holst_files_subdir'], jpg_file_name)
            img_file = self.open_image_file(jpg_file_name, abs_path)
            if img_file is None:
                continue
            width, height = get_file_sizes(img_file)
            self.files_for_preview[jpg_file_name[0:-4] + ".jpeg"] = img_file.resize((width, height), BICUBIC)
            count += 1
            self.set_new_value_of_progress_bar(count)

    def open_image_file(self, img_file_name, abs_path, is_psd=False):
        log_message = "Обрабатываю файл: {0}".format(img_file_name)
        self.set_what_in_work(log_message)
        logging.info(log_message)
        if path.exists(abs_path):
            try:
                if is_psd:
                    psd = PSDImage.open(abs_path)
                else:
                    img = Image.open(abs_path)
                    return img
            except Exception:
                self.output_error("Не удалось открыть файл: {0}".format(img_file_name))
                return None
        else:
            self.output_error("Не удалось найти файл: {0}".format(img_file_name))
            return None
        try:
            # self.set_what_in_work("Конвертирую файл: {0}".format(img_file_name))
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
        self.progress_bar_percent.emit(0)
        self.progress_bar_maximum.emit(len(self.files_for_preview))
        count_for_pb = 0
        for key, val in self.dict_of_class.items():
            cell = 0
            count = 0
            for item in val:
                for file_name, image in item.items():
                    self.what_in_work.emit("Добавляю в превью: Класс {0} ({1})".format(key, file_name))
                    cell += 1
                    count += 1
                    if cell == 1:
                        page = draw_page.draw_page(self.settings['font_regular'], self.settings['font_bold'],
                                                   self.settings['font_italic'])
                        page.draw_name_object(self.settings['object_name'])
                        page.draw_of_klass(key)
                    page.draw_information_of_photo(cell, file_name, self.settings, image)
                    count_for_pb += 1
                    self.progress_bar_percent.emit(count_for_pb)
                    if cell == 4 or count == len(val):
                        page.save_page(self.settings['object_name'], self.settings['path'])
                        # page.__init__()
                        cell = 0

    def remove_old_pdf(self):
        self.set_what_in_work("Удаляю старое превью")
        pdf_files = search_file_with_extension("pdf", self.settings['path'])
        pdf_file_name = self.settings['object_name'] + ".pdf"
        if pdf_file_name in pdf_files:
            logging.info("Удаление старого превью: {0}{1}{2}".format(self.settings['path'], sep, pdf_file_name))
            remove(path.join(self.settings['path'], pdf_file_name))
