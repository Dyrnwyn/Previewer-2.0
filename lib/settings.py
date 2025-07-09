from platform import system
from os import getcwd, sep, path
from json import dumps, loads
from lib.static_method import show_message_box


class PreviewerSettings(object):
    __slots__ =[
                "font_italic", "species", "format", "template", "photo", "number", "school_class", "last_name",
                "id", "summ", "holst", "with_price", "font_regular", "font_bold", "holst_files_subdir",
                "text_for_qr", "qr_error_correct", "bottom_text"
                ]

    def __init__(self):
        self.species: int = 0
        self.format: int = 0
        self.template: int = 0
        self.photo: int = 0
        self.number: int = 0
        self.school_class: int = 0
        self.last_name: int = 0
        self.id: int = 0
        self.summ: int = 0
        self.holst: bool = False
        self.with_price: bool = False
        self.font_regular: str = ""
        self.font_bold: str = ""
        self.font_italic: str = ""
        self.holst_files_subdir: str = ""
        self.text_for_qr: str = ""
        self.qr_error_correct: set = set()
        self.bottom_text: str = ""

        if not path.exists(self.__get_settings_file_path()):
            self.set_default_settings()
        else:
            self.load_settings()

    def set_default_settings(self):
        self.__fill_class_attributes(self.__default_dict_settings())
        self.save_settings()

    def save_settings(self):
        json_txt = dumps(self.__settings_to_dict())
        with open(self.__get_settings_file_path(), 'w') as settings_file:
            settings_file.write(json_txt)
            settings_file.close()

    def load_settings(self):
        with open(self.__get_settings_file_path(), 'r') as settings_file:
            json_text = settings_file.read()
            settings_file.close()
            error_in_settings = False
            dict_default_settings = self.__default_dict_settings()
            if json_text != '':
                settings = loads(json_text)
                for k, v in settings.items():
                    dict_default_settings[k] = settings[k]
                self.__fill_class_attributes(dict_default_settings)
            else:
                self.set_default_settings()

    @staticmethod
    def get_font_path():
        if system() == "Linux":
            return '{0}{1}Font{2}'.format(getcwd(), sep, sep)
        elif system() == "Windows":
            return '{0}{1}{2}{3}'.format(path.expandvars(r'%LOCALAPPDATA%'), sep + 'Microsoft',
                                         sep + 'Windows',
                                         sep + 'Fonts' + sep)

    @staticmethod
    def get_settings_filename() -> str:
        return 'settings.conf'

    @staticmethod
    def get_settings_directory() -> str:
        return path.expanduser("~") + sep + "Previewer2.0" + sep

    def __get_settings_file_path(self):
        return self.get_settings_directory() + self.get_settings_filename()

    def __default_dict_settings(self):
        return {
            'species': 0,
            'format': 1,
            'template': 2,
            'photo': 3,
            'number': 4,
            'class': 5,
            'last_name': 9,
            'id': 11,
            'summ': 12,
            'holst': False,
            'with_price': False,
            'font_regular': self.get_font_path() + 'afuturica.ttf',
            'font_bold': self.get_font_path() + 'afuturicaextrabold.ttf',
            'font_italic': self.get_font_path() + 'afuturicaitalic.ttf',
            'holst_files_subdir': 'renamed_files',
            'text_for_qr': """ST00012|Name=ООО «Объемный мир»|PersonalAcc=40702810631000007404
                                      |BankName=ПАОСБЕРБАНК|BIC=040407627|CorrespAcc=30101810800000000627
                                      |PayeeINN=2464105021|KPP=246001001|PersAcc={id}|Sum={summ}""",
            'qr_error_correct': {'index': 3, 'text': '30%'},
            'bottom_text': "vk.com/omfoto_ru\nОбъемныйМир.рф/parents"
        }

    def __fill_class_attributes(self, dict_settings: dict):
        self.species = dict_settings['species']
        self.format = dict_settings['format']
        self.template = dict_settings['template']
        self.photo = dict_settings['photo']
        self.number = dict_settings['number']
        self.school_class = dict_settings['class']
        self.last_name = dict_settings['last_name']
        self.id = dict_settings['id']
        self.summ = dict_settings['summ']
        self.holst = dict_settings['holst']
        self.with_price = dict_settings['with_price']
        self.font_regular = dict_settings['font_regular']
        self.font_bold = dict_settings['font_bold']
        self.font_italic = dict_settings['font_italic']
        self.holst_files_subdir = dict_settings['holst_files_subdir']
        self.text_for_qr = dict_settings['text_for_qr']
        self.qr_error_correct = dict_settings['qr_error_correct']
        self.bottom_text = dict_settings['bottom_text']

    def __settings_to_dict(self):
        dict_settings = self.__default_dict_settings()
        dict_settings['species'] = self.species
        dict_settings['format'] = self.format
        dict_settings['template'] = self.template
        dict_settings['photo'] = self.photo
        dict_settings['number'] = self.number
        dict_settings['class'] = self.school_class
        dict_settings['last_name'] = self.last_name
        dict_settings['id'] = self.id
        dict_settings['summ'] = self.summ
        dict_settings['holst'] = self.holst
        dict_settings['with_price'] = self.with_price
        dict_settings['font_regular'] = self.font_regular
        dict_settings['font_bold'] = self.font_bold
        dict_settings['font_italic'] = self.font_italic
        dict_settings['holst_files_subdir'] = self.holst_files_subdir
        dict_settings['text_for_qr'] = self.text_for_qr
        dict_settings['qr_error_correct'] = self.qr_error_correct
        dict_settings['bottom_text'] = self.bottom_text
        return dict_settings




