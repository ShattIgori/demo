
import sys, mysql.connector
from PySide6.QtWidgets import *
from PySide6.QtUiTools import *
from PySide6.QtCore import Qt

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.loader = QUiLoader()
        self.db = mysql.connector.connect(host="localhost", user="root", password="Lbhtrnjh_4231", database="cafeteria_db", port=3305)
        self.cart_items = []
        self.login = self.loader.load("login.ui")
        self.catalog = self.loader.load("catalog.ui")
        self.cart = self.loader.load("cart.ui")
        self.success = self.loader.load("success.ui")
        self.setup_login()
        self.setup_catalog()
        self.setup_cart()
        self.setup_success()
        self.login.show()
        sys.exit(self.app.exec())

    def query(self, sql, params=()):
        cur = self.db.cursor(dictionary=True)
        cur.execute(sql, params)
        res = cur.fetchall()
        cur.close()
        return res

    def execute(self, sql, params=()):
        cur = self.db.cursor()
        cur.execute(sql, params)
        self.db.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id

    def setup_login(self):
        self.login.btn_login.clicked.connect(self.auth)

    def auth(self):
        if self.login.lineEdit_2.text() == "admin" and self.login.lineEdit.text() == "123":
            self.load_catalog()
            self.catalog.show()
            self.login.hide()
        else:
            QMessageBox.warning(self.login, "Ошибка", "Неверный логин или пароль")

    def setup_catalog(self):
        self.catalog.btn_to_cart.clicked.connect(lambda: (self.cart.show(), self.catalog.hide(), self.refresh_cart()))
        self.catalog.btn_exit.clicked.connect(lambda: (self.login.show(), self.catalog.hide()))
        self.catalog.lineEdit.textChanged.connect(self.load_catalog)
        self.catalog.comboBox.currentIndexChanged.connect(self.load_catalog)
        self.catalog.radioButton.clicked.connect(self.load_catalog)
        self.catalog.radioButton_2.clicked.connect(self.load_catalog)
        cats = self.query("SELECT * FROM categories")
        self.catalog.comboBox.addItem("Любая категория", None)
        for c in cats: self.catalog.comboBox.addItem(c['name'], c['id'])

    def load_catalog(self):
        layout = self.catalog.scrollAreaWidgetContents.layout()
        while layout.count():
            w = layout.takeAt(0).widget()
            if w: w.deleteLater()
        sql = "SELECT p.*, c.name as cat FROM products p JOIN categories c ON p.category_id=c.id WHERE p.is_active=1"
        params = []
        if self.catalog.lineEdit.text():
            sql += " AND p.name LIKE %s"
            params.append(f"%{self.catalog.lineEdit.text()}%")
        if self.catalog.comboBox.currentData():
            sql += " AND p.category_id=%s"
            params.append(self.catalog.comboBox.currentData())
        sql += " ORDER BY p.price " + ("ASC" if self.catalog.radioButton.isChecked() else "DESC")
        prods = self.query(sql, params)
        for i, p in enumerate(prods):
            card = QFrame()
            card.setFixedSize(200, 250)
            card.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 10px; background: white; }")
            vbox = QVBoxLayout(card)
            img = QLabel("Изображение")
            img.setAlignment(Qt.AlignCenter)
            img.setStyleSheet("background: #eee; border-radius: 5px;")
            img.setFixedHeight(100)
            vbox.addWidget(img)
            vbox.addWidget(QLabel(f"<b>{p['name']}</b>"))
            vbox.addWidget(QLabel(f"<small>{p['description'][:50]}...</small>"))
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"<b>{p['price']} р.</b>"))
            btn = QPushButton("Добавить")
            btn.clicked.connect(lambda _, x=p: self.add_to_cart(x))
            hbox.addWidget(btn)
            vbox.addLayout(hbox)
            card.mousePressEvent = lambda e, x=p: QMessageBox.information(self.catalog, "Инфо", f"{x['name']}\n{x['description']}\nЦена: {x['price']}")
            layout.addWidget(card, i // 4, i % 4)

    def add_to_cart(self, p):
        for item in self.cart_items:
            if item['id'] == p['id']:
                item['qty'] += 1
                return
        p['qty'] = 1
        self.cart_items.append(p)

    def setup_cart(self):
        self.cart.btn_back.clicked.connect(lambda: (self.catalog.show(), self.cart.hide()))
        self.cart.btn_confrim.clicked.connect(self.make_order)
        self.cart.checkBox.stateChanged.connect(lambda s: self.cart.comboBox.setEnabled(not s))
        clients = self.query("SELECT * FROM clients")
        for c in clients: self.cart.comboBox.addItem(c['name'] or c['phone_number'], c['phone_number'])
        self.cart.comboBox_2.addItems(["Наличные", "Карта", "Онлайн"])

    def refresh_cart(self):
        self.cart.tableWidget.setRowCount(len(self.cart_items))
        total = 0
        for i, item in enumerate(self.cart_items):
            sub = float(item['price']) * item['qty']
            total += sub
            self.cart.tableWidget.setItem(i, 0, QTableWidgetItem(item['name']))
            self.cart.tableWidget.setItem(i, 1, QTableWidgetItem(str(item['price'])))
            spin = QSpinBox()
            spin.setValue(item['qty'])
            spin.valueChanged.connect(lambda v, row=i: self.update_qty(row, v))
            self.cart.tableWidget.setCellWidget(i, 2, spin)
            self.cart.tableWidget.setItem(i, 3, QTableWidgetItem(str(sub)))
            btn = QPushButton("Удалить")
            btn.clicked.connect(lambda _, row=i: self.remove_from_cart(row))
            self.cart.tableWidget.setCellWidget(i, 4, btn)
        self.cart.label_5.setText(f"Итого: {total} руб.")

    def update_qty(self, row, v):
        self.cart_items[row]['qty'] = v
        self.refresh_cart()

    def remove_from_cart(self, row):
        self.cart_items.pop(row)
        self.refresh_cart()

    def make_order(self):
        if not self.cart_items: return
        if QMessageBox.question(self.cart, "Заказ", "Оформить?") != QMessageBox.Yes: return
        total = sum(float(i['price']) * i['qty'] for i in self.cart_items)
        pay_id = self.cart.comboBox_2.currentIndex() + 1
        type_id = 1 if self.cart.radioButton.isChecked() else (2 if self.cart.radioButton_2.isChecked() else 3)
        oid = self.execute("INSERT INTO orders (order_number, date_create, type_id, employer_id, total_cost, pay_id) VALUES ((SELECT IFNULL(MAX(order_number),0)+1 FROM orders o2), NOW(), %s, 1, %s, %s)", (type_id, total, pay_id))
        for item in self.cart_items:
            self.execute("INSERT INTO order_shopcase (order_id, product_id, current_count) VALUES (%s,%s,%s)", (oid, item['id'], item['qty']))
        self.cart_items = []
        self.success.show()
        self.cart.hide()

    def setup_success(self):
        self.success.btn_back.clicked.connect(lambda: (self.catalog.show(), self.success.hide()))

if __name__ == "__main__":
    App()
