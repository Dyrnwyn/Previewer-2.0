from os import scandir


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
    if splited_filename[0] == "о":
        species = "объемная"
    elif splited_filename[0] == "п":
        species = "плоская"
    else:
        species = " "
    return species


def get_proportion_from_filename(splited_filename):
    proportions = splited_filename[1]
    if "Кружка" in proportions:
        proportions = "Кружка-термос"
    if "Настенный кален" in proportions:
        proportions = "Настенный к."
    return proportions


def show_message_box_with_question(title_text, message_text):
    from PyQt5 import QtWidgets
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question,
                                    title_text, message_text)
    msg_box.addButton("&Отмена", QtWidgets.QDialogButtonBox.RejectRole)
    msg_box.addButton("&Продолжить", QtWidgets.QDialogButtonBox.AcceptRole)
    msg_box.exec_()
