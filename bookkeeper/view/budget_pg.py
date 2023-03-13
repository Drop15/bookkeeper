"""
Виджет страницы бюджета
"""
from typing import Callable

from PySide6 import QtWidgets, QtCore

from bookkeeper.models.budget import Budget


class BudgetWindow(QtWidgets.QWidget):
    """
    Класс виджета окна, в котором отображается бюджет
    """
    def __init__(self, *args,
                 budgets_getter: Callable | None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.budgets_table = QtWidgets.QTableWidget(3, 3)
        self.budgets_table.setColumnCount(3)
        self.budgets_table.setRowCount(3)
        self.budgets_table.setHorizontalHeaderLabels(
            ["Период", "Расходы за период", "Бюджет на период"]
        )
        self.header = self.budgets_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)

        self.set_budgets(budgets_getter)

    def build_budgets(self, data: list[Budget]) -> None:
        for i, row in enumerate(data):
            self.budgets_table.setItem(
                i, 0,
                QtWidgets.QTableWidgetItem(row.duration)
            )
            self.budgets_table.setItem(
                i, 1,
                QtWidgets.QTableWidgetItem(str(row.amount))
            )
            self.budgets_table.setItem(
                i, 2,
                QtWidgets.QTableWidgetItem(str(row.limits))
            )

    def set_budgets(self, budgets_getter: Callable) -> None:
        if self.budgets_table.itemAt(0, 0) is not None:
            self.layout.removeWidget(self.budgets_table)

        budgets_data = budgets_getter()

        self.budgets_table = QtWidgets.QTableWidget(3, 3)
        self.budgets_table.setColumnCount(3)
        self.budgets_table.setRowCount(3)
        self.budgets_table.setHorizontalHeaderLabels(
            ["Период", "Расходы за период", "Бюджет на период"]
        )
        self.header = self.budgets_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)

        self.build_budgets(budgets_data)
        self.layout.addWidget(self.budgets_table)


class ChangeBudgetWindow(QtWidgets.QWidget):
    """
    Класс виджета изменения бюджета
    """
    def __init__(self, *args,
                 budgets_setter: Callable | None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.change_budget_window_title = QtWidgets.QLabel("Задать Бюджет")

        self.layout.addWidget(self.change_budget_window_title)
        self.layout.addWidget(SetBudgetInput(name="День",
                                             budget_setter=budgets_setter))
        self.layout.addWidget(SetBudgetInput(name="Неделя",
                                             budget_setter=budgets_setter))
        self.layout.addWidget(SetBudgetInput(name="Месяц",
                                             budget_setter=budgets_setter))


class SetBudgetInput(QtWidgets.QWidget):
    """
    Класс виджета ввода бюджета
    """
    def __init__(self, name, *args,
                 budget_setter: Callable | None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.duration = name
        self.setter = budget_setter

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.period = QtWidgets.QLabel(name)
        self.input = QtWidgets.QLineEdit()
        self.save_btn = QtWidgets.QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_btn_clicked)

        self.layout.addWidget(self.period)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.save_btn)

    @QtCore.Slot()
    def save_btn_clicked(self) -> None:
        """
        Функция нажатия на кнопку сохранения
        """
        limits = float(self.input.text())
        self.setter(limits, self.duration)


class BudgetPage(QtWidgets.QWidget):
    """
    Класс виджета страницы бюджета
    """
    def __init__(self, *args,
                 get_handler: Callable | None,
                 set_handler: Callable | None,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.budget_window = BudgetWindow(budgets_getter=get_handler)
        self.layout.addWidget(self.budget_window)

        self.change_budget_window = ChangeBudgetWindow(budgets_setter=set_handler)
        self.layout.addWidget(self.change_budget_window)
