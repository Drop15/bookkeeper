"""
Модель бюджета по категории расходов
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Budget:
    """
    Бюджет по категории товаров, хранит срок (duration), на который установлен бюджет,
    id категории, к которой относится бюджет (category),
    и сумма бюджета на данный срок (amount)
    pk - id записи в базе данных
    """

    amount: float
    limits: float
    duration: str
    end: datetime
    start: datetime = datetime.now()
    pk: int = 0
