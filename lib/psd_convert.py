import logging
from os import remove, walk as os_walk
from previewer2_logick import Previewer
from PyQt6.QtCore import pyqtSignal
from lib.static_method import get_list_of_psd_files, save_file

class PSDWorker(Previewer):
    progress_bar_psd_percent = pyqtSignal(int)
    progress_bar_psd_maximum = pyqtSignal(int)

    logging.basicConfig(filename='previewer.log', filemode='w', format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.INFO)

    def __init__(self, parent, object_path, psd_file, convert, replace_layer, layer, previous_layer):
        super().__init__(parent=parent, settings="", object_path=object_path, object_name="")
        self.psd_file = psd_file
        self.convert = convert
        self.replace_layer = replace_layer
        self.layer = layer
        self.previous_layer = previous_layer

    def run(self):
        if self.convert:
            for root, dirs, files in os_walk(self.object_path):
                self.object_path = root
                self.files_for_preview.clear()
                self.psd_files = get_list_of_psd_files(root)
                if len(self.psd_files) == 0:
                    continue
                self.convert_psd(False)
                save_file(root, self.files_for_preview)
            self.compose_result.emit(self.get_compose_result("Завершение конвертации psd",
                                                             "Файлы успешно конвертированы"))
        elif self.replace_layer:
            files_without_layer = self.replace_layer_in_psd_file()
            if len(files_without_layer) == 0:
                self.compose_result.emit(self.get_compose_result("Завершение замены слоев",
                                                                 "Слои успешно заменены"))
            else:
                msg = "Слои успешно заменены.\n"
                msg += "Файлы в которых слой был добавлен в начало/конец\n"
                msg += "и требуется редактирование со стороны пользователя:\n"
                for file in files_without_layer:
                    msg += file + "\n"
                self.compose_result.emit(self.get_compose_result("Завершение замены слоев", msg))

    def replace_layer_in_psd_file(self):
        from psd_tools import PSDImage
        from os.path import join as path_join
        from lib.static_method import save_psd_file

        self.initialize_progress_bar(self.count_psd_files())
        pg_count = 0

        files_without_layer = []
        for root, dirs, files in os_walk(self.object_path):
            psd_files = get_list_of_psd_files(root)
            for psd_file in psd_files:
                pg_count += 1
                self.set_new_value_of_progress_bar(pg_count)
                self.what_in_work.emit("Обрабатывается файл: {}".format(psd_file))
                if self.psd_file != psd_file:
                    psd_img = PSDImage.open(path_join(root, psd_file))
                    layer_replaced = False
                    for layer in psd_img:
                        if layer.name == self.layer.name:
                            self.layer.visible = layer.visible
                            layer_index = psd_img.index(layer)
                            psd_img.remove(layer)
                            psd_img.insert(layer_index, self.layer)
                            save_psd_file(psd_img, root, psd_file)
                            layer_replaced = True
                            break
                    if not layer_replaced and self.previous_layer is not None:
                        for cur_prev_layer in psd_img:
                            if cur_prev_layer.name == self.previous_layer.name:
                                layer_index = psd_img.index(cur_prev_layer)
                                psd_img.insert(layer_index + 1, self.layer)
                                save_psd_file(psd_img, root, psd_file)
                                layer_replaced = True
                                break
                    if not layer_replaced:
                        psd_img.insert(0, self.layer)
                        save_psd_file(psd_img, root, psd_file)
                        files_without_layer.append(path_join(root, psd_file))
        return files_without_layer

    def count_psd_files(self):
        psd_overall = 0
        for root, dirs, files in os_walk(self.object_path):
            psd_files = get_list_of_psd_files(root)
            psd_overall += len(psd_files)
        return psd_overall