import sys
from PySide6.QtWidgets import *
from PySide6.QtUiTools import *
from PySide6.QtCore import Qt

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.loader = QUiLoader()

        # Тестовые данные вместо базы данных
        self.test_data = {
            'categories': [
                {'id': 1, 'name': 'Напитки'},
                {'id': 2, 'name': 'Выпечка'},
                {'id': 3, 'name': 'Салаты'},
                {'id': 4, 'name': 'Основные блюда'}
            ],
            'products': [
                {'id': 1, 'name': 'Капучино', 'description': 'Ароматный кофе с молочной пенкой', 'price': '180.00', 'category_id': 1, 'is_active': 1},
                {'id': 2, 'name': 'Латте', 'description': 'Нежный кофейный напиток с молоком', 'price': '200.00', 'category_id': 1, 'is_active': 1},
                {'id': 3, 'name': 'Круассан', 'description': 'Слоеная выпечка с шоколадом', 'price': '120.00', 'category_id': 2, 'is_active': 1},
                {'id': 4, 'name': 'Салат Цезарь', 'description': 'Салат с курицей, сухариками и соусом цезарь', 'price': '350.00', 'category_id': 3, 'is_active': 1},
                {'id': 5, 'name': 'Паста Карбонара', 'description': 'Паста с беконом и сливочным соусом', 'price': '420.00', 'category_id': 4, 'is_active': 1},
                {'id': 6, 'name': 'Чай зеленый', 'description': 'Ароматный зеленый чай', 'price': '150.00', 'category_id': 1, 'is_active': 1},
                {'id': 7, 'name': 'Чизкейк', 'description': 'Нежный десерт из творожного сыра', 'price': '280.00', 'category_id': 2, 'is_active': 1},
                {'id': 8, 'name': 'Греческий салат', 'description': 'Салат с овощами и сыром фета', 'price': '320.00', 'category_id': 3, 'is_active': 1}
            ],
            'clients': [
                {'name': 'Иван Иванов', 'phone_number': '+79161234567'},
                {'name': 'Мария Петрова', 'phone_number': '+79266543210'},
                {'name': None, 'phone_number': '+79031234567'}
            ],
            'orders': []  # Для хранения созданных заказов
        }

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
        """Заглушка для SQL-запросов SELECT"""
        print(f"[DEBUG] Выполняется запрос: {sql} с параметрами: {params}")

        # Обработка запросов к категориям
        if "categories" in sql.lower():
            return self.test_data['categories']

        # Обработка запросов к клиентам
        elif "clients" in sql.lower():
            return self.test_data['clients']

        # Обработка запросов к продуктам
        elif "products" in sql.lower():
            prods = self.test_data['products'].copy()

            # Фильтрация по активности
            prods = [p for p in prods if p['is_active'] == 1]

            # Фильтрация по названию
            for param in params:
                if isinstance(param, str) and '%' in param:
                    search_term = param.replace('%', '').lower()
                    if search_term:
                        prods = [p for p in prods if search_term in p['name'].lower()]

            # Фильтрация по категории
            for i, param in enumerate(params):
                if "category_id" in sql.lower() and i == len(params) - 1:
                    if param:
                        prods = [p for p in prods if p['category_id'] == param]

            # Добавляем информацию о категории
            for prod in prods:
                for cat in self.test_data['categories']:
                    if cat['id'] == prod['category_id']:
                        prod['cat'] = cat['name']
                        break

            return prods

        return []

    def execute(self, sql, params=()):
        """Заглушка для SQL-запросов INSERT/UPDATE"""
        print(f"[DEBUG] Выполняется команда: {sql} с параметрами: {params}")

        # Обработка создания заказа
        if "INSERT INTO orders" in sql.upper():
            import random
            import datetime

            order_id = len(self.test_data['orders']) + 1
            order_number = random.randint(1000, 9999)
            date_create = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Извлекаем параметры
            type_id = params[0] if len(params) > 0 else 1
            total = params[1] if len(params) > 1 else 0
            pay_id = params[2] if len(params) > 2 else 1

            order = {
                'id': order_id,
                'order_number': order_number,
                'date_create': date_create,
                'type_id': type_id,
                'total': total,
                'pay_id': pay_id
            }

            self.test_data['orders'].append(order)
            print(f"[DEBUG] Создан заказ #{order_number}")
            return order_id

        # Обработка добавления товаров в заказ
        elif "INSERT INTO order_shopcase" in sql.upper():
            print(f"[DEBUG] Добавлены товары в заказ {params[0]}")
            return len(self.test_data['orders'])

        return 1

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

        # Загрузка категорий из тестовых данных
        cats = self.test_data['categories']
        self.catalog.comboBox.addItem("Любая категория", None)
        for c in cats:
            self.catalog.comboBox.addItem(c['name'], c['id'])

    def load_catalog(self):
        layout = self.catalog.scrollAreaWidgetContents.layout()
        while layout.count():
            w = layout.takeAt(0).widget()
            if w: w.deleteLater()

        # Получаем фильтры
        search_text = self.catalog.lineEdit.text()
        category_id = self.catalog.comboBox.currentData()
        sort_asc = self.catalog.radioButton.isChecked()

        # Фильтруем товары
        prods = self.test_data['products'].copy()

        # Фильтр по активности
        prods = [p for p in prods if p['is_active'] == 1]

        # Фильтр по названию
        if search_text:
            prods = [p for p in prods if search_text.lower() in p['name'].lower()]

        # Фильтр по категории
        if category_id:
            prods = [p for p in prods if p['category_id'] == category_id]

        # Сортировка
        prods.sort(key=lambda x: float(x['price']), reverse=not sort_asc)

        # Добавляем информацию о категории
        for prod in prods:
            for cat in self.test_data['categories']:
                if cat['id'] == prod['category_id']:
                    prod['cat'] = cat['name']
                    break

        # Отображаем товары
        for i, p in enumerate(prods):
            card = QFrame()
            card.setFixedSize(200, 250)
            card.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 10px; background: white; }")
            vbox = QVBoxLayout(card)

            # Изображение товара (заглушка)
            img = QLabel("🍕" if p['category_id'] == 2 else
                        "☕" if p['category_id'] == 1 else
                        "🥗" if p['category_id'] == 3 else "🍝")
            img.setAlignment(Qt.AlignCenter)
            img.setStyleSheet("font-size: 40px; background: #eee; border-radius: 5px;")
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

            # Клик по карточке для подробной информации
            card.mousePressEvent = lambda e, x=p: QMessageBox.information(
                self.catalog, "Информация о товаре",
                f"<b>{x['name']}</b><br>"
                f"{x['description']}<br>"
                f"<br><b>Цена:</b> {x['price']} руб.<br>"
                f"<b>Категория:</b> {x.get('cat', 'Не указана')}"
            )

            layout.addWidget(card, i // 4, i % 4)

    def add_to_cart(self, p):
        for item in self.cart_items:
            if item['id'] == p['id']:
                item['qty'] += 1
                return
        p = p.copy()  # Создаем копию, чтобы не менять оригинал
        p['qty'] = 1
        self.cart_items.append(p)

    def setup_cart(self):
        self.cart.btn_back.clicked.connect(lambda: (self.catalog.show(), self.cart.hide()))
        self.cart.btn_confrim.clicked.connect(self.make_order)
        self.cart.checkBox.stateChanged.connect(lambda s: self.cart.comboBox.setEnabled(not s))

        # Загрузка клиентов из тестовых данных
        clients = self.test_data['clients']
        self.cart.comboBox.addItem("Новый клиент", "")
        for c in clients:
            name = c['name'] or c['phone_number']
            self.cart.comboBox.addItem(name, c['phone_number'])

        # Методы оплаты
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
            spin.setMinimum(1)
            spin.setMaximum(99)
            spin.valueChanged.connect(lambda v, row=i: self.update_qty(row, v))
            self.cart.tableWidget.setCellWidget(i, 2, spin)

            self.cart.tableWidget.setItem(i, 3, QTableWidgetItem(f"{sub:.2f}"))

            btn = QPushButton("❌")
            btn.clicked.connect(lambda _, row=i: self.remove_from_cart(row))
            self.cart.tableWidget.setCellWidget(i, 4, btn)

        self.cart.label_5.setText(f"Итого: {total:.2f} руб.")

    def update_qty(self, row, v):
        self.cart_items[row]['qty'] = v
        self.refresh_cart()

    def remove_from_cart(self, row):
        self.cart_items.pop(row)
        self.refresh_cart()

    def make_order(self):
        if not self.cart_items:
            QMessageBox.warning(self.cart, "Корзина пуста", "Добавьте товары в корзину перед оформлением заказа")
            return

        if QMessageBox.question(self.cart, "Подтверждение заказа", "Оформить заказ?") != QMessageBox.Yes:
            return

        # Расчет общей стоимости
        total = sum(float(i['price']) * i['qty'] for i in self.cart_items)

        # Получение данных о заказе
        pay_method = self.cart.comboBox_2.currentText()

        # Определение типа заказа
        if self.cart.radioButton.isChecked():
            order_type = "На месте"
            type_id = 1
        elif self.cart.radioButton_2.isChecked():
            order_type = "Самовывоз"
            type_id = 2
        else:
            order_type = "Доставка"
            type_id = 3

        # Информация о клиенте
        if self.cart.checkBox.isChecked():
            client_info = "Новый клиент"
        else:
            client_name = self.cart.comboBox.currentText()
            client_info = f"Клиент: {client_name}"

        # Создание заказа (заглушка)
        order_id = self.execute("INSERT INTO orders (order_number, date_create, type_id, employer_id, total_cost, pay_id) VALUES (0, NOW(), %s, 1, %s, %s)",
                               (type_id, total, self.cart.comboBox_2.currentIndex() + 1))

        # Добавление товаров в заказ
        for item in self.cart_items:
            self.execute("INSERT INTO order_shopcase (order_id, product_id, current_count) VALUES (%s,%s,%s)",
                        (order_id, item['id'], item['qty']))

        # Показ информации о заказе
        order_details = (
            f"<b>Заказ успешно оформлен!</b><br><br>"
            f"<b>Номер заказа:</b> #{order_id}<br>"
            f"<b>Тип заказа:</b> {order_type}<br>"
            f"<b>Способ оплаты:</b> {pay_method}<br>"
            f"<b>{client_info}</b><br>"
            f"<b>Общая сумма:</b> {total:.2f} руб.<br><br>"
            f"<i>Спасибо за заказ!</i>"
        )

        QMessageBox.information(self.cart, "Заказ оформлен", order_details)

        # Очистка корзины и переход
        self.cart_items = []
        self.success.show()
        self.cart.hide()

    def setup_success(self):
        self.success.btn_back.clicked.connect(lambda: (self.catalog.show(), self.success.hide()))

        # Добавляем информацию о последнем заказе
        if hasattr(self, 'test_data') and self.test_data['orders']:
            last_order = self.test_data['orders'][-1]
            self.success.label_2.setText(
                f"Заказ #{last_order['order_number']} оформлен!\n"
                f"Сумма: {last_order['total']:.2f} руб.\n\n"
                f"Спасибо за покупку!"
            )

if __name__ == "__main__":
    App()
