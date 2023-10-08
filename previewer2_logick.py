import logging
import draw_page
from PyQt5.QtCore import QThread, pyqtSignal
from os import scandir, path, remove, sep
from re import findall
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
    @staticmethod
    def search_file_with_extension(file_extension, folder=""):
        files_list = []
        with scandir(folder) as file_list:
            for file in file_list:
                if not file.name.startswith('.') and file.is_file() and \
                        findall(r"^.*\." + file_extension + "*", file.name):
                    files_list.append(file.name)
        return files_list

    # def search_psd_file_for_convert_in_object_path(self):
    #     self.what_in_work.emit("Ищу psd файлы в папке объекта")
    #     with scandir(self.settings['path']) as file_list:
    #         for file in file_list:
    #             if not file.name.startswith('.') and file.is_file() and \
    #                     findall(r"^.*\." + "psd" + "*", file.name):
    #                 self.psd_files_for_convert.append(file.name)

    def convert_psd(self):
        # Конвертируем psd файлы, конвертируем его в RGB и ресайзим
        # до размера 900 px
        self.progress_bar_maximum.emit(len(self.settings['psd_files']))
        self.progress_bar_percent.emit(0)
        count = 0
        base_size = 900
        for psd_file_name in self.settings['psd_files']:
            logging.info("Открываю файл: {0}".format(psd_file_name))
            if path.exists(self.settings['path'] + sep + psd_file_name):
                try:
                    psd = PSDImage.open(self.settings['path'] + sep + psd_file_name)
                except Exception:
                    logging.error("Не удалось открыть файл: {0}".format(psd_file_name))
                    self.missed_files.emit(self.missed_files_msg.format(psd_file_name))
            else:
                logging.error("Не удалось найти файл: {0}".format(psd_file_name))
                self.missed_files.emit(self.missed_files_msg.format(psd_file_name))
                continue
            try:
                self.what_in_work.emit("Конвертирую файл: {0}".format(psd_file_name))
                rgb_png = psd.composite().convert("RGB")
            except Exception as E:
                logging.error("Не удалось конвертировать: {0}".format(psd_file_name))
                self.missed_files.emit(self.missed_files_msg.format(psd_file_name))
                continue
            x, y = rgb_png.size
            if x > y:
                width = base_size
                height = int(width / x * y)
            elif y > x:
                height = base_size
                width = int(height / y * x)
            else:
                height = 590
                width = 590
            self.files_for_preview[psd_file_name[0:-4] + ".jpeg"] = rgb_png.resize((width, height), BICUBIC)
            count += 1
            self.progress_bar_percent.emit(count)

    def convert_jpg(self):
        # Конвертируем psd файлы, конвертируем его в RGB и ресайзим
        # до размера 900 px
        self.progress_bar_maximum.emit(len(self.settings['holst_files']))
        self.progress_bar_percent.emit(0)
        count = 0
        base_size = 900
        for jpg_file_name in self.settings['holst_files']:

            self.what_in_work.emit("Конвертирую файл: {0}".format(jpg_file_name))
            jpg_file_name_abs_path = path.join(self.settings['path'], self.settings['holst_files_subdir'],
                                               jpg_file_name)
            if path.exists(jpg_file_name_abs_path):
                logging.info("Открываю файл: {0}".format(jpg_file_name))
                jpg = Image.open(jpg_file_name_abs_path)
            else:
                logging.error("Не удалось открыть файл: {0}".format(jpg_file_name))
                self.missed_files.emit(self.missed_files_msg.format(jpg_file_name))
                continue
            x, y = jpg.size
            if x > y:
                width = base_size
                height = int(width / x * y)
            elif y > x:
                height = base_size
                width = int(height / y * x)
            else:
                height = 590
                width = 590
            self.files_for_preview[jpg_file_name[0:-4] + ".jpeg"] = jpg.resize((width, height), BICUBIC)
            count += 1
            self.progress_bar_percent.emit(count)

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
        self.what_in_work.emit("Удаляю старое превью")
        pdf_files = self.search_file_with_extension("pdf", self.settings['path'])
        pdf_file_name = self.settings['object_name'] + ".pdf"
        if pdf_file_name in pdf_files:
            logging.info("Удаление старого превью: {0}{1}{2}".format(self.settings['path'], sep, pdf_file_name))
            remove(self.settings['path'] + sep + pdf_file_name)
