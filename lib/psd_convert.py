import logging
from os import remove, walk as os_walk
from previewer2_logick import Previewer
from lib.static_method import get_list_of_psd_files, replace_layer_in_psd_file, save_file

class PSDWorker(Previewer):
    logging.basicConfig(filename='previewer.log', filemode='w', format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.INFO)

    def __init__(self, parent, object_path, psd_file, convert, replace_layer, layer):
        super().__init__(parent=parent, settings="", object_path=object_path, object_name="")
        self.psd_file = psd_file
        self.convert = convert
        self.replace_layer = replace_layer
        self.layer = layer
        self.missed_files_msg = "Ошибка при обработке: {0}\n"

    def run(self):
        if self.convert:
            for root, dirs, files in os_walk(self.object_path):
                self.psd_files = get_list_of_psd_files(root)
                self.convert_psd(False)
                save_file(root, self.files_for_preview)
            self.compose_result.emit(self.get_compose_result("Завершение конвертации psd",
                                                             "Файлы успешно конвертированы"))
        elif self.replace_layer:
            replace_layer_in_psd_file(self.object_path, self.psd_file, self.layer)
            self.compose_result.emit(self.get_compose_result("Завершение замены слоев",
                                                             "Слои успешно заменены"))
