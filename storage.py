from copy import deepcopy
from math import isfinite


class Storage:
    def __init__(self):
        self.__items = {}

    @property
    def items(self) -> dict:
        return deepcopy(self.__items)

    def add_items(self, name: str, quantity: int, price: float) -> None:
        name = name.strip().lower()

        if not name:
            raise ValueError("Название товара не может быть пустым")
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if not isfinite(price) or price < 0:
            raise ValueError("Цена должна быть конечной и неотрицательной")

        if name in self.__items:
            self.__items[name]["quantity"] += quantity
            self.__items[name]["price"] = price
        else:
            self.__items[name] = {
                "quantity": quantity,
                "price": price,
            }

    def set_quantity(self, name: str, quantity: int) -> None:
        name = name.strip().lower()

        if name not in self.__items:
            raise ValueError("Такого товара нет на складе")
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")

        self.__items[name]["quantity"] = quantity

    def remove_items(self, name: str) -> None:
        name = name.strip().lower()

        if name not in self.__items:
            raise ValueError("Такого товара нет на складе")

        del self.__items[name]

    def get_current_item(self, name: str) -> dict:
        name = name.strip().lower()

        if name not in self.__items:
            raise ValueError("Такого товара нет на складе")

        return self.__items[name].copy()

    def take_items(self, name: str, quantity: int) -> None:
        name = name.strip().lower()

        if name not in self.__items:
            raise ValueError("Такого товара нет на складе")
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if quantity > self.__items[name]["quantity"]:
            raise ValueError("Недостаточно товара на складе")

        self.__items[name]["quantity"] -= quantity

    def show_items(self) -> None:
        if not self.__items:
            print("Склад пуст")
            return

        print("Товары на складе:")
        for name, info in self.__items.items():
            print(f"- {name}: {info['quantity']} шт., {info['price']} руб.")