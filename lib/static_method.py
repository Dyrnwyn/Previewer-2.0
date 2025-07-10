import os.path
from os import scandir

import psd_tools.api.layers
from PyQt6.QtWidgets import QMessageBox
from os import path, mkdir
from psd_tools import PSDImage


def get_parametrs_from_file_name(file_name):
    splited_filename = file_name.split("_")
    parametrs = {'species': get_species_from_filename(splited_filename),
                 'proportions': get_proportion_from_filename(splited_filename),
                 'template': get_template_from_file_name(splited_filename),
                 'photo': get_photo_from_file_name(splited_filename),
                 'number': get_number_from_file_name(splited_filename),
                 'cost': get_cost_from_file_name(splited_filename),
                 'id_client': get_id_client_from_file_name(splited_filename),
                 'last_name': get_last_name_from_file_name(splited_filename)
                 }
    return parametrs





# def get_file_list_in_path_used_re_template(path_for_search, template):
#     from re import compile as re_compile
#     file_list = []
#     re_pattern = re_compile(r"^.*\." + template + "*")
#     for file in scandir(path_for_search):
#         if not file.name.startswith('.') and file.is_file() and \
#                 re_pattern.findall(file.name):
#             file_list.append(file.name)
#     return file_list
def save_file(object_path, files):
    for file_name, img in files.items():
        img.save(os.path.join(object_path, file_name))

def get_file_sizes(img_file, base_size=900):
    x, y = img_file.size
    if x > y:
        width = base_size
        height = int(width / x * y)
    elif y > x:
        height = base_size
        width = int(height / y * x)
    else:
        height = 590
        width = 590
    return width, height

def get_list_of_psd_files(path_for_search):
    return search_file_with_extension("psd", path_for_search)

def get_list_of_pdf_files(path_for_search):
    return search_file_with_extension("pdf", path_for_search)

def get_list_of_xls_files(path_for_search):
    return search_file_with_extension("xls.*", path_for_search)

def get_list_of_jpeg_files(path_for_search):
    return search_file_with_extension("jp.*", path_for_search)

def search_file_with_extension(file_extension, folder=""):
    from re import compile as re_compile
    files_list = []
    re_pattern = re_compile(r"^.*\." + file_extension)
    with scandir(folder) as file_list:
        for file in file_list:
            if not file.name.startswith('.') and file.is_file() and \
                    re_pattern.findall(file.name):
                files_list.append(file.name)
    return files_list


def get_species_from_filename(splited_filename):
    species = get_position_parametr(splited_filename, 0, '')
    if species == "о":
        species = "объемная"
    elif species == "п":
        species = "плоская"
    else:
        species = " "
    return species


def get_proportion_from_filename(splited_filename):
    proportions = get_position_parametr(splited_filename, 1, '0x0')
    if "Кружка" in proportions:
        proportions = "Кружка-термос"
    if "Настенный кален" in proportions:
        proportions = "Настенный к."
    return proportions


def get_template_from_file_name(splited_filename):
    return get_position_parametr(splited_filename, 2, '0000')


def get_photo_from_file_name(splited_filename):
    return get_position_parametr(splited_filename, 3, '0000')


def get_number_from_file_name(splited_filename):
    number = get_position_parametr(splited_filename, 4, '')
    if "[" in number:
        number = number[1:-1]
    return number


def get_id_client_from_file_name(splited_filename):
    return get_position_parametr(splited_filename, 11, '')


def get_last_name_from_file_name(splited_filename):
    return get_position_parametr(splited_filename, 9, '')


def get_cost_from_file_name(splited_filename):
    return get_position_parametr(splited_filename, 8, '0')


def get_position_parametr(splited_filename, position_number, default_value=''):
    if (len(splited_filename) - 1) < position_number:
        return default_value
    return splited_filename[position_number]


def show_message_box_with_question(title_text, message_text):
    from PyQt5 import QtWidgets
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                    title_text, message_text)
    msg_box.addButton("&Отмена", QtWidgets.QDialogButtonBox.RejectRole)
    msg_box.addButton("&Продолжить", QtWidgets.QDialogButtonBox.AcceptRole)
    msg_box.exec_()


def show_message_box(title_text, message_text):
    msg_box = QMessageBox()
    msg_box.addButton(QMessageBox.StandardButton.Ok)
    msg_box.setWindowTitle(title_text)
    msg_box.setText(message_text)
    msg_box.exec()
    # msg_box = QtWidgets.QMessageBox(parent=parent)
    # msg_box(QtWidgets.QMessageBox.Icon.Warning, title_text, message_text,
    #         buttons=QtWidgets.QMessageBox.StandardButton.Ok)
    #
    # msg_box.exec()


def find_files_for_preview(with_price, path_for_searching):
    refuse_files = []
    file_name_length = 7
    if with_price:
        file_name_length = 12
    file_list = search_file_with_extension(path_for_searching, 'psd')
    psd_files = []
    for file_name in file_list:
        if (len(file_name.split('_'))) < file_name_length:
            refuse_files.append(file_name)
        else:
            psd_files.append(file_name)
    if len(refuse_files) > 0:
        message_text = "В файлах:\n{0}указана не вся информация для формирования превью.\n" \
                       + "Файлы будут пропущены"
        files = ""
        for f in refuse_files:
            files += f + "\n"
        show_message_box("Ошибка", message_text.format(files))
    return psd_files


def create_dir(creating_path):
    if not path.exists(creating_path):
        mkdir(creating_path)

def get_layers_name_from_psd(full_name):
    psd_img = PSDImage.open(full_name)
    layer_list = []
    for layer in psd_img:
        layer_dict = {layer.name: layer}
        layer_list.append(layer_dict)
    return layer_list

def replace_layer_in_psd_file(work_path, psd_file_name, psd_layer, previous_layer):
    files_without_layer = []
    psd_files = get_list_of_psd_files(work_path)
    for psd_file in psd_files:
        if psd_file_name != psd_file:
            psd_img = PSDImage.open(os.path.join(work_path, psd_file))
            layer_replaced = False
            for layer in psd_img:
                if layer.name == psd_layer.name:
                    layer_index = psd_img.index(layer)
                    psd_img.remove(layer)
                    psd_img.insert(layer_index, psd_layer)
                    psd_img.save(os.path.join(work_path, psd_file + "_copy"))
                    layer_replaced = True
                    break
            if not layer_replaced and previous_layer is not None:
                for cur_prev_layer in psd_img:
                    if cur_prev_layer.name == previous_layer.name:
                        layer_index = psd_img.index(cur_prev_layer)
                        psd_img.insert(layer_index + 1, psd_layer)
                        psd_img.save(os.path.join(work_path, psd_file + "_copy"))
                        layer_replaced = True
                        break
            if not layer_replaced:
                psd_img.insert(0, psd_layer)
                psd_img.save(os.path.join(work_path, psd_file + "_copy"))
                files_without_layer.append(os.path.join(work_path, psd_file))
    return files_without_layer







