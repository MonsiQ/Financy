import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, \
    QHBoxLayout, QCalendarWidget, QSplitter, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate

class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.balance = 0
        self.incomes = 0
        self.expenses = 0
        self.history = []
        self.undo_stack = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Учет финансов')
        self.setGeometry(100, 100, 800, 400)
        self.setFixedSize(800, 700)  # Устанавливаем фиксированный размер окна

        splitter = QSplitter(self)

        # Левая часть - основной интерфейс
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)

        self.balance_label = QLabel('Баланс: 0 р.', left_widget)

        self.amount_label = QLabel('Сумма:', left_widget)
        self.amount_edit = QLineEdit(left_widget)

        self.description_label = QLabel('Описание:', left_widget)
        self.description_edit = QLineEdit(left_widget)

        self.add_income_button = QPushButton('Добавить доход', left_widget)
        self.add_income_button.clicked.connect(self.add_income)

        self.add_expense_button = QPushButton('Добавить расход', left_widget)
        self.add_expense_button.clicked.connect(self.add_expense)

        self.undo_button = QPushButton('Отменить', left_widget)
        self.undo_button.clicked.connect(self.undo)

        self.save_button = QPushButton('Сохранить', left_widget)
        self.save_button.clicked.connect(self.save_data)

        self.load_button = QPushButton('Загрузить', left_widget)
        self.load_button.clicked.connect(self.load_data)

        self.date_label = QLabel('Дата:', left_widget)
        self.date_calendar = QCalendarWidget(left_widget)
        self.date_calendar.setGridVisible(True)
        self.date_calendar.setSelectedDate(QDate.currentDate())

        left_layout.addWidget(self.balance_label)
        left_layout.addWidget(self.amount_label)
        left_layout.addWidget(self.amount_edit)
        left_layout.addWidget(self.description_label)
        left_layout.addWidget(self.description_edit)
        left_layout.addWidget(self.date_label)
        left_layout.addWidget(self.date_calendar)
        left_layout.addWidget(self.add_income_button)
        left_layout.addWidget(self.add_expense_button)
        left_layout.addWidget(self.undo_button)
        left_layout.addWidget(self.save_button)
        left_layout.addWidget(self.load_button)

        # Правая часть - история операций и статистика
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)

        self.history_label = QLabel('История операций:', right_widget)
        self.history_textedit = QTextEdit(right_widget)
        self.history_textedit.setReadOnly(True)

        self.statistics_label = QLabel('Статистика:', right_widget)
        self.statistics_textedit = QTextEdit(right_widget)
        self.statistics_textedit.setReadOnly(True)

        right_layout.addWidget(self.history_label)
        right_layout.addWidget(self.history_textedit)
        right_layout.addWidget(self.statistics_label)
        right_layout.addWidget(self.statistics_textedit)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        self.setLayout(layout)
        self.show()

        # Применение стилей CSS
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                color: #f0f0f0;
                font-family: "Segoe UI", sans-serif;
            }

            QPushButton {
                background-color: #3a3a3a;
                color: #f0f0f0;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #2c2c2c;
            }

            QLabel {
                font-size: 18px;
            }

            QTextEdit, QLineEdit {
                font-size: 16px;
                border: 2px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
                background-color: #2f2f2f;
                color: #f0f0f0;
            }

            QCalendarWidget {
                background-color: #2f2f2f;
                color: #f0f0f0;
                border: 2px solid #1f1f1f;
                border-radius: 5px;
            }

            QCalendarWidget QWidget {
                alternate-background-color: #1f1f1f;
            }

            QCalendarWidget QToolButton {
                background-color: #3a3a3a;
                color: #f0f0f0;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #2c2c2c;
            }

            .QTextEdit-green {
                color: #2ecc71;
            }

            .QTextEdit-red {
                color: #e74c3c;
            }
        """)

    def add_income(self):
        amount_str = self.amount_edit.text()
        description = self.description_edit.text()
        date = self.date_calendar.selectedDate().toString("dd.MM.yyyy")

        try:
            amount = float(amount_str)
        except ValueError:
            return

        self.balance += amount
        self.incomes += amount
        self.history.append(f'+: {amount} р. ({description}) - {date}')
        self.undo_stack.append(('income', amount, description, date))
        self.update_ui()

    def add_expense(self):
        amount_str = self.amount_edit.text()
        description = self.description_edit.text()
        date = self.date_calendar.selectedDate().toString("dd.MM.yyyy")

        try:
            amount = float(amount_str)
        except ValueError:
            return

        if amount > self.balance:
            return

        self.balance -= amount
        self.expenses += amount
        self.history.append(f'-: {amount} р. ({description}) - {date}')
        self.undo_stack.append(('expense', amount, description, date))
        self.update_ui()

    def undo(self):
        if self.undo_stack:
            operation, amount, description, date = self.undo_stack.pop()
            if operation == 'income':
                self.balance -= amount
                self.incomes -= amount
            elif operation == 'expense':
                self.balance += amount
                self.expenses -= amount
            self.history.pop()
            self.update_ui()

    def save_data(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Сохранить данные', '', 'JSON Files (*.json)')
        if file_name:
            data = {
                'balance': self.balance,
                'incomes': self.incomes,
                'expenses': self.expenses,
                'history': self.history
            }
            with open(file_name, 'w') as file:
                json.dump(data, file)
            QMessageBox.information(self, 'Успешно', 'Данные успешно сохранены!')

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Загрузить данные', '', 'JSON Files (*.json)')
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    data = json.load(file)
                self.balance = data['balance']
                self.incomes = data['incomes']
                self.expenses = data['expenses']
                self.history = data['history']
                self.update_ui()
                QMessageBox.information(self, 'Успешно', 'Данные успешно загружены!')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Произошла ошибка при загрузке данных: {str(e)}')

    def update_ui(self):
        self.amount_edit.clear()
        self.description_edit.clear()
        self.balance_label.setText(f'Баланс: {self.balance} рублей')
        self.history_textedit.setPlainText('\n'.join(self.history))
        self.statistics_textedit.setPlainText(
            f'Доходы: {self.incomes} рублей\n'
            f'Расходы: {self.expenses} рублей\n'
            f'Итог: {self.balance} рублей'
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    tracker = FinanceTracker()
    sys.exit(app.exec_())