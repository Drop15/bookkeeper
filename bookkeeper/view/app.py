"""
Класс приложения на PyQT (view)
"""
import sys
from PySide6 import QtWidgets
from functools import partial
from typing import Callable

from bookkeeper.view.expenses_pg import ExpensesPage
from bookkeeper.view.categories_pg import CategoriesPage
from bookkeeper.view.budget_pg import BudgetPage


def handle_error(widget, handler):
    def inner(*args, **kwargs):
        try:
            handler(*args, **kwargs)
        except Exception as ex:
            QtWidgets.QMessageBox.critical(widget, 'Ошибка', str(ex))

    return inner


class PageManagerToolbar(QtWidgets.QWidget):
    def __init__(self, *args, parent: type | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.parent = parent

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.expensesBtn = QtWidgets.QPushButton(text="Расходы")
        self.expensesBtn.clicked.connect(partial(self.set_page, 0))
        self.layout.addWidget(self.expensesBtn)

        self.budgetBtn = QtWidgets.QPushButton(text="Бюджет")
        self.budgetBtn.clicked.connect(partial(self.set_page, 1))
        self.layout.addWidget(self.budgetBtn)

        self.categoriesBtn = QtWidgets.QPushButton(text="Категории расходов")
        self.categoriesBtn.clicked.connect(partial(self.set_page, 2))
        self.layout.addWidget(self.categoriesBtn)

    def set_page(self, page_index=0) -> None:
        self.parent.page_layout.setCurrentIndex(page_index)


class MainWindow(QtWidgets.QWidget):
    get_category_handler: Callable | None
    add_category_handler: Callable | None
    edit_category_handler: Callable | None
    delete_category_handler: Callable | None

    get_expenses_handler: Callable | None
    get_categories_handler: Callable | None
    add_expense_handler: Callable | None
    edit_expense_handler: Callable | None
    edit_budgets_handler: Callable | None
    get_db_expense_handler: Callable | None

    get_budgets_handler: Callable | None
    set_budgets_handler: Callable | None

    def __init__(self, *args,
                 category_handlers: list[Callable | None],
                 expenses_handlers: list[Callable | None],
                 budgets_handlers: list[Callable | None],
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.register_category_handlers(category_handlers)
        self.register_expenses_handlers(expenses_handlers)
        self.register_budgets_handlers(budgets_handlers)

        self.setWindowTitle("The BookKeeper App")
        self.setGeometry(50, 50, 800, 900)

        self.budget_page = BudgetPage(
            get_handler=self.get_budgets_handler,
            set_handler=self.set_budgets_handler
        )
        self.expenses_page = ExpensesPage(
            get_handler=self.get_expenses_handler,
            get_categories_handler=self.get_categories_handler,
            add_handler=self.add_expense_handler,
            edit_handler=self.edit_expense_handler,
            edit_budgets_handler=self.edit_budgets_handler,
            get_db_expense_handler=self.get_db_expense_handler
        )
        self.categories_page = CategoriesPage(
            get_handler=self.get_category_handler,
            add_handler=self.add_category_handler,
            edit_handler=self.edit_category_handler,
            delete_handler=self.delete_category_handler
        )
        self.menuBarWidget = PageManagerToolbar(parent=self)

        self.layout = QtWidgets.QVBoxLayout()

        self.page_layout = QtWidgets.QStackedLayout()
        self.page_layout.addWidget(self.expenses_page)
        self.page_layout.addWidget(self.budget_page)
        self.page_layout.addWidget(self.categories_page)

        self.layout.addWidget(self.menuBarWidget)
        self.layout.addLayout(self.page_layout)
        self.setLayout(self.layout)

    def register_category_handlers(self, handlers: list[Callable | None]) -> None:
        self.get_category_handler = handlers[0]
        self.add_category_handler = handlers[1]
        self.edit_category_handler = handlers[2]
        self.delete_category_handler = handlers[3]

    def register_expenses_handlers(self, handlers: list[Callable | None]) -> None:
        self.get_expenses_handler = handlers[0]
        self.get_categories_handler = handlers[1]
        self.add_expense_handler = handlers[2]
        self.edit_expense_handler = handlers[3]
        self.edit_budgets_handler = handlers[4]
        self.get_db_expense_handler = handlers[5]

    def register_budgets_handlers(self, handlers: list[Callable | None]) -> None:
        self.get_budgets_handler = handlers[0]
        self.set_budgets_handler = handlers[1]


class View:
    app: QtWidgets.QApplication
    window: MainWindow
    category_handlers: list[Callable | None]
    expenses_handlers: list[Callable | None]
    budgets_handlers: list[Callable | None]

    def __init__(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)

    def start_app(self) -> None:
        self.window = MainWindow(
            category_handlers=self.category_handlers,
            expenses_handlers=self.expenses_handlers,
            budgets_handlers=self.budgets_handlers
        )
        self.window.show()
        sys.exit(self.app.exec())

    def register_handlers(self, handlers_obj: dict[str, list[Callable | None]]):
        self.category_handlers = handlers_obj["category"]
        self.expenses_handlers = handlers_obj["expenses"]
        self.budgets_handlers = handlers_obj["budget"]
