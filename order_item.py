class OrderItem:
    def __init__(self, name: str, quantity: int, price: float):
        if not name.strip():
            raise ValueError("Название позиции не может быть пустым")
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")

        self.__name = name.strip()
        self.__quantity = quantity
        self.__price = price

    @property
    def name(self) -> str:
        return self.__name

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def price(self) -> float:
        return self.__price

    def get_total_price(self) -> float:
        return self.__quantity * self.__price

    def check_price(self) -> bool:
        if self.__price < 0:
            raise ValueError("Цена не может быть отрицательной")

        return True

    def check_quantity(self) -> bool:
        if self.__quantity <= 0:
            raise ValueError("Количество должно быть положительным")

        return True
