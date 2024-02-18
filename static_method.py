from os import scandir


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


def get_file_list_in_path_used_re_template(path_for_search, template):
    from re import compile as re_compile
    file_list = []
    re_pattern = re_compile(template)
    for file in scandir(path_for_search):
        if not file.name.startswith('.') and file.is_file() and \
                re_pattern.fullmatch(file.name):
            file_list.append(file.name)
    return file_list


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


def search_file_with_extension(file_extension, folder=""):
    from re import findall
    files_list = []
    with scandir(folder) as file_list:
        for file in file_list:
            if not file.name.startswith('.') and file.is_file() and \
                    findall(r"^.*\." + file_extension + "*", file.name):
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
