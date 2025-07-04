def information_top():
    return ("Через банкомат\n"
            "Сбербанка, Сбербанк\n"
            "онлайн:")


def information_main():
    return ("1. Найдите нашу\n"
            "организацию по\n"
            "ИНН\n"
            "2. Введите № заказа\n\n"
            "3. Проверьте\n"
            "правильность заказа и\n"
            "произведите оплату")


def inn():
    return "2464105021"


def thank_text():
    return ("Спасибо за заказ! Заходите к нам на сайт")


def sites_text():
    return ("ОбъемныйМир.рф(вкладка меню ""Родителям"")")


def text_above_qr():
    return "Через Сбербанк онлайн по \nQR-коду (быстрая оплата)"

def data_qr(persacc, summ):
    return """ST00012|Name=ООО «Объемный мир»|PersonalAcc=40702810631000007404|BankName=ПАОСБЕРБАНК|BIC=040407627|CorrespAcc=30101810800000000627|PayeeINN=2464105021|KPP=246001001|PersAcc=""" + persacc + """|Sum=""" + summ