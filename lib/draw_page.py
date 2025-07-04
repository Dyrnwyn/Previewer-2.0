from os.path import join as joint_path

from PIL.Image import new as new_page, Transpose, Image
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype as load_font
from qrcode import ERROR_CORRECT_H
from qrcode.main import QRCode

from lib import positions, texts
from lib.static_method import get_parametrs_from_file_name


class Page(object):
    """docstring for draw_page"""

    def __init__(self, font_regular, font_bold, font_italic):
        # Инициализируем новый лист, шрифт
        self.font_regular = font_regular
        self.font_bold = font_bold
        self.font_italic = font_italic
        self.page = new_page("RGB", (2480, 3508), color=(255, 255, 255))
        self.draw = Draw(self.page, "RGB")
        self.font = load_font(self.font_regular, 30)
        self.draw_line_page()
        self.draw_title()

    def change_font(self, font_name, font_size=40):
        self.font = load_font(font_name, font_size)

    def draw_line_page(self):  # Разметка страницы на ячейки
        # -------------horizontal line--------------------
        self.draw.line([(60, 400), (2420, 400)], fill=0, width=5)
        self.draw.line([(60, 1924), (2420, 1924)], fill=0, width=5)
        self.draw.line([(60, 3448), (2420, 3448)], fill=0, width=5)
        # -------------vertical line----------------------
        self.draw.line([(2420, 400), (2420, 3448)], fill=0, width=5)
        self.draw.line([(1210, 400), (1210, 3448)], fill=0, width=5)
        self.draw.line([(60, 400), (60, 3448)], fill=0, width=5)
        self.draw.text((60, 40), "Class")

    def draw_information_of_photo(self, cell, photo_parametrs, settings, image):
        self.add_img(cell, image, settings)
        parameters = ("Вид: " + photo_parametrs['species'] + "\n" +
                      "Размер: " + photo_parametrs['proportions'] + "\n" +
                      "Шаблон: " + photo_parametrs['template'] + "\n" +
                      "Фото: " + photo_parametrs['photo'] + "\n" +
                      "Кол-во:" + photo_parametrs['number'] + "\n"
                      )
        if settings.with_price:
            if photo_parametrs['id_client'] != "":
                pass
            self.draw_preview_with_price(cell, parameters,
                                         photo_parametrs['cost'],
                                         photo_parametrs['id_client'],
                                         photo_parametrs['last_name'])
        else:
            self.draw_preview_without_price(cell, parameters, settings, photo_parametrs['cost'])

    def draw_preview_without_price(self, cell, parameters, settings, cost):
        self.change_font(self.font_regular, font_size=45)
        dict_xy = positions.text_without_price()
        self.draw.text(dict_xy[cell], parameters, font=self.font, fill=0)
        self.draw_cost(cell, cost, False)
        self.draw_bottom_text(cell, settings)

    def draw_preview_with_price(self, cell, parameters, cost, id_client, last_name):
        self.change_font(self.font_regular, font_size=25)
        dict_xy = positions.text_with_price()
        self.draw_id_information(cell, id_client)
        self.draw.text(dict_xy[cell], parameters, font=self.font, fill=(0, 0, 0))
        self.draw_sites(cell)
        self.add_qr(cell, cost, id_client)
        self.draw_text_pay_or_on_center_pager(cell)

    def draw_title(self):
        self.change_font(self.font_regular, font_size=35)
        self.draw.text((60, 30), "класс/группа", font=self.font, fill=0)
        font_width = self.font.getlength("Наименование Объекта")
        self.draw.text((self.page.width / 2 - font_width / 2, 30),
                       "Наименование Объекта", font=self.font, fill=0)

    def draw_name_object(self, name_object="Без имени"):
        # В методе выводим название объекта
        self.change_font(self.font_bold, font_size=70)
        font_width = self.font.getlength(name_object)
        self.draw.text((self.page.width / 2 - font_width / 2, 100),
                       name_object, font=self.font, fill=0)

    def draw_of_klass(self, name_klass="00"):
        # Рисуем класс/группу
        self.change_font(self.font_regular, font_size=70)
        self.draw.text((60, 100), name_klass, font=self.font, fill=0)

    def draw_last_name(self, last_name, numb_cell):
        self.change_font(self.font_regular, font_size=40)
        dict_xy = positions.last_name()
        self.draw.text(dict_xy[numb_cell], last_name, font=self.font, fill=0)

    def draw_id_information(self, cell_number, id_client):
        dict_xy_top = positions.id_information_top()
        dict_xy_main = positions.id_information_main()
        dict_xy_inn = positions.id_information_inn()
        dict_xy_order_number = positions.id_information_order_number()

        text_information_top = texts.information_top()
        text_information_main = texts.information_main()
        text_inn = texts.inn()

        order_number = id_client
        self.change_font(self.font_bold, font_size=30)
        self.draw.text(dict_xy_top[cell_number], text_information_top, font=self.font, fill=0)
        self.change_font(self.font_regular, font_size=30)
        self.draw.text(dict_xy_main[cell_number], text_information_main, font=self.font, fill=0)
        self.draw.text(dict_xy_inn[cell_number], text_inn, font=self.font, fill=(255, 0, 0))
        self.draw.text(dict_xy_order_number[cell_number], order_number, font=self.font, fill=(255, 0, 0))

    def draw_cost(self, cell, cost, with_id):
        if with_id:
            dict_xy = positions.cost_with_id()
        else:
            dict_xy = positions.cost_without_id()
        cost_txt = "Сумма: " + cost
        self.draw.text(dict_xy[cell], cost_txt, font=self.font, fill=(255, 0, 0))

    def draw_bottom_text(self, cell, settings):
        dict_xy = positions.bottom_text_without_id()
        self.draw.text(dict_xy[cell], settings.bottom_text, font=self.font, fill=(0, 0, 255))

    def draw_sites(self, cell_number):
        self.change_font(self.font_regular, font_size=30)
        dict_xy_thank = positions.thank_text()
        thank_text = texts.thank_text()
        self.draw.text(dict_xy_thank[cell_number], thank_text, font=self.font, fill=(0, 0, 0))

        self.change_font(font_name=self.font_bold, font_size=30)
        dict_xy_site = positions.site_text()
        sites_text = texts.sites_text()
        self.draw.text(dict_xy_site[cell_number], sites_text, font=self.font, fill=(25, 0, 200))

    def draw_text_pay_or_on_center_pager(self, cell):
        self.change_font(self.font_bold, font_size=40)
        dict_xy_pay = positions.text_pay()
        dict_xy_or = positions.text_or()
        text_or = "ИЛИ"
        text_pay = "ОПЛАТА"
        self.draw.text(dict_xy_pay[cell], text_pay, font=self.font, fill=(0, 0, 0))
        self.draw.text(dict_xy_or[cell], text_or, font=self.font, fill=(0, 0, 0))

    def add_img(self, cell, img, settings):
        # метод вывода фото изделия в ячейки
        dict_xy = positions.img()
        if img.height > img.width and settings.with_price:
            img = img.transpose(method=Transpose.ROTATE_90)
        self.page.paste(img, dict_xy[cell])

    def add_qr(self, cell, summ, persacc):
        if persacc != '' or summ != '' or persacc != ' ' or summ != ' ':
            self.add_text_above_qr(cell)
            if not isinstance(summ, int):
                summ = 0
            summ = str(int(summ) * 100)
            dict_xy = positions.qr(cell)
            qr_code = QRCode(version=1, error_correction=ERROR_CORRECT_H, box_size=5, border=1)
            qr_code.add_data(texts.data_qr(persacc, summ))
            qr_image = qr_code.make_image()
            box = (dict_xy[0], dict_xy[1])
            if not isinstance(qr_image, Image):
                qr_image = qr_image.convert()
            self.page.paste(qr_image, box)

    def add_text_above_qr(self, cell):
        self.change_font(self.font_regular, font_size=30)
        dict_xy = positions.text_above_qr()
        text_above_qr = texts.text_above_qr()
        self.draw.text(dict_xy[cell], text_above_qr, font=self.font, fill=(0, 0, 0))

    def save_page(self, object_name, object_path):
        # Добавляем страницу в pdf файл, если файла нет, создаем его
        object_name_with_ext = '{0}{1}'.format(object_name, ".pdf")
        try:
            self.page.save(joint_path(object_path, object_name_with_ext) , append=True, resolution=300)
        except FileNotFoundError:
            self.page.save(joint_path(object_path, object_name_with_ext), resolution=300)
        except PermissionError as e:
            fl_object = open("pypreviewer_err.txt", "w")
            fl_object.write(e)
            fl_object.close()
