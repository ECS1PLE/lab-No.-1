from abc import ABC, abstractmethod

class Client:
    def __init__(self, id: int, name: str, phone: str, address: str):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address

    def change_address(self, new_address: str) -> None:
        self.address = new_address


class Courier:
    def __init__(self, id: int, name: str, phone: str):
        self.id = id
        self.name = name
        self.phone = phone
        self.is_available = True

    def accept_order(self, order: "Order") -> None:
        if self.is_available:
            order.assign_courier(self)
            self.is_available = False
        else:
            raise Exception("Курьер недоступен")


class OrderItem:
    def __init__(self, name: str, quantity: int, price: float):
        self.name = name
        self.quantity = quantity
        self.price = price

    def get_total_price(self) -> float:
        return self.quantity * self.price


class DeliveryMethod(ABC):
    @abstractmethod
    def calculate_cost(self) -> float:
        ...

    @abstractmethod
    def estimate_time(self) -> str:
        ...

class Order:
    def __init__(
        self,
        id: int,
        client: Client,
        address: str,
        items: list[OrderItem],
        delivery_method: DeliveryMethod,
    ):
        self.id = id
        self.client = client
        self.address = address
        self.items = items
        self.delivery_method = delivery_method
        self.courier: Courier | None = None
        self.status = "создан"

    def assign_courier(self, courier: Courier) -> None:
        self.courier = courier

    def calculate_total_price(self) -> float:
        return sum(item.get_total_price() for item in self.items)

    def change_status(self, new_status: str) -> None:
        self.status = new_status