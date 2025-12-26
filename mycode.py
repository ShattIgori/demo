import sys
from PySide6.QtWidgets import *
from PySide6.QtUiTools import *

app = QApplication(sys.argv)
loader = QUiLoader()

login = loader.load("login.ui")
catalog = loader.load("catalog.ui")
cart = loader.load ("cart.ui")
success = loader.load ("success.ui")

btn_login = login.findChild(QPushButton, "btn_login")
if btn_login:
    def step1():
        catalog.show()
        login.hide()
btn_login.clicked.connect(step1)



btn_to_cart = catalog.findChild(QPushButton, "btn_to_cart")
if btn_to_cart:
    def step2():
        cart.show()
        catalog.hide()
btn_to_cart.clicked.connect(step2)


btn_exit = catalog.findChild(QPushButton, "btn_exit")
if btn_exit:
    def step3():
        login.show()
        catalog.hide()
btn_exit.clicked.connect(step3)



btn_confrim = cart.findChild(QPushButton, "btn_confrim")
if btn_confrim:
    def step4():
        success.show()
        cart.hide()
btn_confrim.clicked.connect(step4)



btn_back = cart.findChild(QPushButton, "btn_back")
if btn_back:
    def step5():
        catalog.show()
        cart.hide()
btn_back.clicked.connect(step5)

btn_back_success = success.findChild(QPushButton, "btn_back")
if btn_back_success:
    def step6():
        catalog.show()
        success.hide()
btn_back_success.clicked.connect(step6)


login.show()

app.exec()
