import qrcode
from PIL import Image, ImageDraw, ImageFont
from os import sep
import logging

class draw_page(object):
    """docstring for draw_page"""

    def __init__(self, font_regular, font_bold, font_italic):
        # Инициализируем новый лист, шрифт
        self.font_regular = font_regular
        self.font_bold = font_bold
        self.font_italic = font_italic
        self.page = Image.new("RGB", (2480, 3508), color=(255, 255, 255))
        self.draw = ImageDraw.Draw(self.page, "RGB")
        self.font = ImageFont.truetype(self.font_regular, 30)
        self.draw_line_page()
        self.draw_title()

    def change_font(self, font_name, font_size=40):
        self.font = ImageFont.truetype(font_name, font_size)

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

    def draw_information_of_photo(self, cell, file_name, settings, image):
        self.add_img(cell, image, settings)
        split_file_name = file_name.split("_")
        if split_file_name[0] == "о":
            species = "объемная"
        elif split_file_name[0] == "п":
            species = "плоская"
        else:
            species = " "
        proportions = split_file_name[1]
        if "Кружка" in proportions:
            proportions = "Кружка-термос"
        if ("Настенный кален" in proportions):
            proportions = "Настенный к."
        template = split_file_name[2]
        photo = split_file_name[3]
        number = split_file_name[4]
        cost = split_file_name[8]
        if "[" in number:
            number = number[1:-1]
        parameters = ("Вид: " + species + "\n" +
                     "Размер: " + proportions + "\n" +
                     "Шаблон: " + template + "\n" +
                     "Фото: " + photo + "\n" +
                     "Кол-во:" + number + "\n"
                     )
        if settings['with_price']:
            cost = split_file_name[12].split(".")[0]
            id_client = split_file_name[11]
            last_name = split_file_name[9]
            self.draw_preview_with_price(cell, parameters, cost, id_client, last_name)
        else:
            self.draw_preview_without_price(cell, parameters)
            self.draw_cost(cell, cost, False)

    def draw_preview_without_price(self, cell, parameters):
        self.change_font(self.font_regular, font_size=45)
        dict_xy = {1: (120, 1525),
                   2: (1270, 1525),
                   3: (120, 3075),
                   4: (1270, 3075)
                   }
        self.draw.text(dict_xy[cell], parameters, font=self.font, fill=0)

    def draw_preview_with_price(self, cell, parameters, cost, id_client, last_name):
        self.change_font(self.font_regular, font_size=25)
        dict_xy = {1: (550, 1150),
                   2: (1700, 1150),
                   3: (550, 2650),
                   4: (1700, 2650)
                   }
        self.draw_id_information(cell, id_client)
        self.draw.text(dict_xy[cell], parameters, font=self.font, fill=(0, 0, 0))
        self.draw_sites(cell)
        self.add_qr(cell, cost, id_client)
        self.draw_text_pay_or_on_center_pager(cell)

    def draw_title(self):
        self.change_font(self.font_regular, font_size=35)
        self.draw.text((60, 30), "класс/группа", font=self.font, fill=0)
        font_width = self.font.getsize("Наименование Объекта")[0]
        self.draw.text((self.page.width / 2 - font_width / 2, 30),
                       "Наименование Объекта", font=self.font, fill=0)

    def draw_name_object(self, nameObject="Без имени"):
        # В методе выводим название объекта
        self.change_font(self.font_bold, font_size=70)
        font_width = self.font.getsize(nameObject)[0]
        self.draw.text((self.page.width / 2 - font_width / 2, 100),
                       nameObject, font=self.font, fill=0)

    def draw_of_klass(self, nameKlass="00"):
        # Рисуем класс/группу
        self.change_font(self.font_regular, font_size=70)
        self.draw.text((60, 100), nameKlass, font=self.font, fill=0)

    def draw_last_name(self, last_name, numb_cell):
        self.change_font(self.font_regular, font_size=40)
        dict_xy = {1: (80, 400),
                  2: (1220, 400),
                  3: (80, 1925),
                  4: (1220, 1925)
                  }
        self.draw.text(dict_xy[numb_cell], last_name, font=self.font, fill=0)

    def draw_id_information(self, cell_number, id_client):

        dict_xy_top = {1: (70, 1365),
                       2: (1250, 1365),
                       3: (70, 2915),
                       4: (1250, 2915)}
        dict_xy_main = {1: (70, 1470),
                        2: (1250, 1470),
                        3: (70, 3020),
                        4: (1250, 3020)}
        dict_xy_inn = {1: (150, 1540),
                     2: (1325, 1540),
                     3: (150, 3090),
                     4: (1325, 3090)}
        dict_xy_order_number = {1: (75, 1610),
                             2: (1250, 1610),
                             3: (75, 3160),
                             4: (1250, 3160)}
        text_information_top = ("Через банкомат\n"
                                "Сбербанка, Сбербанк\n"
                                "онлайн:")
        text_information_main = ("1. Найдите нашу\n"
                                 "организацию по\n"
                                 "ИНН\n"
                                 "2. Введите № заказа\n\n"
                                 "3. Проверьте\n"
                                 "правильность заказа и\n"
                                 "произведите оплату")
        text_inn = "2464105021"
        order_number = id_client
        self.change_font(self.font_bold, font_size=30)
        self.draw.text(dict_xy_top[cell_number], text_information_top, font=self.font, fill=0)
        self.change_font(self.font_regular, font_size=30)
        self.draw.text(dict_xy_main[cell_number], text_information_main, font=self.font, fill=0)
        self.draw.text(dict_xy_inn[cell_number], text_inn, font=self.font, fill=(255, 0, 0))
        self.draw.text(dict_xy_order_number[cell_number], order_number, font=self.font, fill=(255, 0, 0))

    def draw_cost(self, cell, cost, with_id):
        if with_id:
            dict_x_yid_nmbr = {1: (73, 1802),
                               2: (1223, 1802),
                               3: (73, 3328),
                               4: (1223, 3328)
                              }
        else:
            dict_x_yid_nmbr = {1: (120, 1800),
                               2: (1270, 1800),
                               3: (120, 3328),
                               4: (1270, 3328)
                               }
        cost_txt = "Сумма: " + cost
        self.draw.text(dict_x_yid_nmbr[cell], cost_txt, font=self.font, fill=(255, 0, 0))

    def draw_sites(self, cell_number):
        self.change_font(self.font_regular, font_size=30)
        dict_xy_thank = {1: (450, 1800),
                         2: (1575, 1800),
                         3: (450, 3330),
                         4: (1575, 3330)}
        thank_text = ("Спасибо за заказ! Заходите к нам на сайт")
        self.draw.text(dict_xy_thank[cell_number], thank_text, font=self.font, fill=(0, 0, 0))

        self.change_font(font_name=self.font_bold, font_size=30)
        dict_xy_site = {1: (325, 1850),
                        2: (1475, 1850),
                        3: (325, 3380),
                        4: (1475, 3380)
                  }
        sites = ("ОбъемныйМир.рф(вкладка меню ""Родителям"")")
        self.draw.text(dict_xy_site[cell_number], sites, font=self.font, fill=(25, 0, 200))

    def draw_text_pay_or_on_center_pager(self, cell):
        self.change_font(self.font_bold, font_size=40)
        dict_xy_pay = {1: (550, 1350),
                     2: (1700, 1350),
                     3: (550, 2900),
                     4: (1700, 2900)}
        dict_xy_or = {1: (585, 1600),
                    2: (1735, 1600),
                    3: (585, 3100),
                    4: (1735, 3100)}
        text_or = "ИЛИ"
        text_pay = "ОПЛАТА"
        self.draw.text(dict_xy_pay[cell], text_pay, font=self.font, fill=(0, 0, 0))
        self.draw.text(dict_xy_or[cell], text_or, font=self.font, fill=(0, 0, 0))

    def add_img(self, cell, img, settings):
        # метод вывода фото изделия в ячейки
        dict_xy = {1: (220, 475),
                  2: (1370, 475),
                  3: (220, 1975),
                  4: (1370, 1975)
                  }
        if img.height > img.width and settings['with_price']:
            img = img.transpose(method=Image.ROTATE_90)
        self.page.paste(img, dict_xy[cell])

    def add_qr(self, cell, summ, persacc):
        if persacc != '' or summ != '' or persacc != ' ' or summ != ' ':
            self.add_text_over_qr(cell)
            dictXY = {1: (800, 1400),
                      2: (2000, 1400),
                      3: (800, 2930),
                      4: (2000, 2930)
                      }
            qr_image = qrcode.QRCode(version=1,
                                     error_correction=qrcode.ERROR_CORRECT_H,
                                     box_size=5,
                                     border=1)
            summ = str(int(summ) * 100)
            qr_image.add_data("""ST00012|Name=ООО «Объемный мир»|PersonalAcc=40702810631000007404|BankName=ПАОСБЕРБАНК|BIC=040407627|CorrespAcc=30101810800000000627|PayeeINN=2464105021|KPP=246001001|PersAcc=""" + persacc + """|Sum=""" + summ)
            self.page.paste(qr_image.make_image(fill_color="black", back_color="white"), dictXY[cell])

    def add_text_over_qr(self, cell):
        self.change_font(self.font_regular, font_size=30)
        dict_xy = {1: (825, 1320),
                  2: (2025, 1320),
                  3: (825, 2850),
                  4: (2025, 2850)
                  }
        text_over_qr = "Через Сбербанк онлайн по \n" \
                       "QR-коду (быстрая оплата)"
        self.draw.text(dict_xy[cell], text_over_qr, font=self.font, fill=(0, 0, 0))

    def save_page(self, object_name, object_path):
        # Добавляем страницу в pdf файл, если файла нет, создаем его
        try:
            self.page.save('{0}{1}{2}'.format(object_path, sep, object_name) + ".pdf", append=True, resolution=300)
        except FileNotFoundError:
            self.page.save('{0}{1}{2}'.format(object_path, sep, object_name) + ".pdf", resolution=300)
        except PermissionError as e:
            fl_object = open("pypreviewer_err.txt", "w")
            fl_object.write(e)
            fl_object.close()
