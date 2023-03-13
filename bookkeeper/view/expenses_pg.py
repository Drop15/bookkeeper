"""
Виджет для отображения страницы списка расходов в окне приложения
"""
from datetime import datetime
from PySide6 import QtWidgets, QtCore
from typing import Callable

from bookkeeper.models.expense import Expense


class CategoryComboBox(QtWidgets.QWidget):
    def __init__(self, *args, category_list_getter: Callable, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.category_box = QtWidgets.QComboBox()
        self.update_categories(category_list_getter=category_list_getter)

    def update_categories(self, category_list_getter: Callable) -> None:
        self.layout.removeWidget(self.category_box)

        self.category_box = QtWidgets.QComboBox()
        categories = category_list_getter()
        for category in categories:
            self.category_box.addItem(category)

        self.layout.addWidget(self.category_box)


class ExpensesList(QtWidgets.QWidget):
    expenses_table: QtWidgets.QTableWidget

    def __init__(self, *args,
                 expenses_getter: Callable | None,
                 expenses_editor: Callable | None,
                 budgets_editor: Callable | None,
                 db_expense_getter: Callable | None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.editor = expenses_editor
        self.setter = expenses_getter
        self.budgets_editor = budgets_editor
        self.db_expense_getter = db_expense_getter

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expenses_title = QtWidgets.QLabel("Последние расходы")
        self.layout.addWidget(self.expenses_title)

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(20)
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        self.header = self.expenses_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.set_expenses(expenses_getter)

    def build_expenses(self, data: list[Expense]) -> None:
        for i, row in enumerate(data):
            self.expenses_table.setItem(
                i, 0,
                QtWidgets.QTableWidgetItem(
                    datetime.strptime(
                        row.expense_date, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y"))
            )
            self.expenses_table.setItem(
                i, 1,
                QtWidgets.QTableWidgetItem(str(row.amount))
            )
            self.expenses_table.setItem(
                i, 2,
                QtWidgets.QTableWidgetItem(str(row.category).capitalize())
            )
            self.expenses_table.setItem(
                i, 3,
                QtWidgets.QTableWidgetItem(str(row.comment))
            )

    def set_expenses(self, expenses_getter: Callable) -> None:
        if self.expenses_table.itemAt(0, 0) is not None:
            self.layout.removeWidget(self.expenses_table)

        expenses_data = expenses_getter()

        self.expenses_table = QtWidgets.QTableWidget(4, len(expenses_data))
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(len(expenses_data))
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        self.header = self.expenses_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.build_expenses(expenses_data)
        self.expenses_table.itemChanged.connect(self.table_item_changed)
        self.layout.addWidget(self.expenses_table)

    @QtCore.Slot()
    def table_item_changed(self, item):
        table_position = self.expenses_table.indexFromItem(item)
        row, column = table_position.row(), table_position.column()

        pk = row + 1
        old_value = self.db_expense_getter(pk)
        amount = old_value.amount
        category = old_value.category
        expense_date = old_value.expense_date
        comment = old_value.comment

        try:
            amount = float(self.expenses_table.item(row, 1).text())
            category = self.expenses_table.item(row, 2).text()
            expense_date = datetime.strptime(
                self.expenses_table.item(row, 0).text(), "%d-%m-%Y"
            )
            comment = self.expenses_table.item(row, 3).text()
            if column == 1:
                self.budgets_editor(value=-old_value.amount + amount, date=expense_date)
            print("table item changed: ",
                  pk, " with amount ", amount,
                  " and category ", category,
                  " and expense date ", expense_date,
                  " and comment ", comment)
        except ValueError as e:
            self.set_expenses(self.setter)
            QtWidgets.QMessageBox.critical(self, 'Ошибка', str(e))

        finally:
            self.editor(pk, amount, category, expense_date, comment)


class AddAmountElement(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.add_amount_input = QtWidgets.QLineEdit()
        self.add_amount_input.setPlaceholderText('Введите сумму, которую вы потратили')
        self.add_expense_date = QtWidgets.QLineEdit(datetime.now().strftime('%d-%m-%Y'))
        self.add_expense_date.setPlaceholderText(
            'Формат: day-month-year'
        )

        self.layout.addWidget(self.add_amount_input)
        self.layout.addWidget(QtWidgets.QLabel("Дата покупки"))
        self.layout.addWidget(self.add_expense_date)


class ChooseCategoryElement(QtWidgets.QWidget):
    def __init__(self, *args, category_list_getter: Callable, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.choose_category_label = QtWidgets.QLabel("Категория")
        self.layout.addWidget(self.choose_category_label)

        self.category_box = CategoryComboBox(category_list_getter=category_list_getter)
        self.layout.addWidget(self.category_box)


class AddCommentElement(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.add_comment_input = QtWidgets.QTextEdit()
        self.add_comment_input.setPlaceholderText('Введите комментарий')

        self.layout.addWidget(self.add_comment_input)


class ElementAddExpense(QtWidgets.QWidget):
    def __init__(self, *args,
                 get_category_list: Callable,
                 adder: Callable,
                 budgets_editor: Callable,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.adder = adder
        self.budgets_editor = budgets_editor

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_expense_title = QtWidgets.QLabel("Добавить новую запись:")
        self.add_btn = QtWidgets.QPushButton(text="Добавить")
        self.add_btn.clicked.connect(self.save_btn_clicked)

        self.add_amount = AddAmountElement()
        self.choose_category = ChooseCategoryElement(
            category_list_getter=get_category_list)
        self.add_comment = AddCommentElement()

        self.layout.addWidget(self.add_expense_title)
        self.layout.addWidget(self.add_amount)
        self.layout.addWidget(self.choose_category)
        self.layout.addWidget(self.add_comment)
        self.layout.addWidget(self.add_btn)

    @QtCore.Slot()
    def save_btn_clicked(self):
        try:
            try:
                amount = float(self.add_amount.add_amount_input.text())
            except ValueError:
                raise ValueError("Введите сумму числами")
            try:
                date = datetime.strptime(
                    self.add_amount.add_expense_date.text(), "%d-%m-%Y"
                )
            except ValueError:
                raise ValueError("Введите дату числами в формате день-месяц-год")
            category = self.choose_category.category_box.category_box.currentText()
            comment = self.add_comment.add_comment_input.toPlainText()
            print("add expense:\namount ", amount,
                  " date ", date, " category ", category,
                  " comment ", comment)
            self.adder(amount, date, category, comment)
            self.budgets_editor(value=amount, date=date)
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, 'Ошибка', str(e))


class ExpensesPage(QtWidgets.QWidget):
    def __init__(self, *args,
                 get_handler: Callable | None,
                 get_categories_handler: Callable | None,
                 add_handler: Callable | None,
                 edit_handler: Callable | None,
                 edit_budgets_handler: Callable | None,
                 get_db_expense_handler: Callable | None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expenses_list = ExpensesList(
            expenses_getter=get_handler,
            expenses_editor=edit_handler,
            budgets_editor=edit_budgets_handler,
            db_expense_getter=get_db_expense_handler
        )
        self.layout.addWidget(self.expenses_list)

        self.add_expense = ElementAddExpense(
            get_category_list=get_categories_handler,
            adder=add_handler,
            budgets_editor=edit_budgets_handler
        )
        self.layout.addWidget(self.add_expense)
