from client import Client
from constants import (
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    STATUS_CREATED,
    STATUS_DELIVERED,
    STATUS_IN_TRANSIT,
    STATUS_READY_FOR_PICKUP,
)
from courier import Courier
from delivery_methods import DeliveryMethod
from order_item import OrderItem
from status_flow import STATUS_FLOW


class Order:
    def __init__(
        self,
        order_id: int,
        client: Client,
        address: str,
        items: list[OrderItem],
        delivery_method: DeliveryMethod,
    ):
        if order_id <= 0:
            raise ValueError("ID заказа должен быть положительным")
        if not address.strip():
            raise ValueError("Адрес доставки не может быть пустым")
        self.__id = order_id
        self.__client = client
        self.__address = address.strip()
        self.__items = list(items)
        self.__delivery_method = delivery_method
        self.__courier: Courier | None = None
        self.__status = STATUS_CREATED

        self.check_items()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def client(self) -> Client:
        return self.__client

    @property
    def address(self) -> str:
        return self.__address

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self.__items)

    @property
    def delivery_method(self) -> DeliveryMethod:
        return self.__delivery_method

    @property
    def courier(self) -> Courier | None:
        return self.__courier

    @property
    def status(self) -> str:
        return self.__status

    def add_item(self, item: OrderItem) -> None:
        if self.__status != STATUS_CREATED:
            raise ValueError(
                "Позиции можно добавлять только в созданный заказ"
            )

        if item.check_price() and item.check_quantity():
            self.__items.append(item)

    def assign_courier(self, courier: Courier) -> None:
        if self.__status not in [STATUS_CREATED, STATUS_CONFIRMED]:
            raise ValueError(
                "Курьера можно назначить только до отправки заказа"
            )

        if not self.__delivery_method.requires_courier:
            raise ValueError("Самовывоз не требует курьера")

        if self.__courier is not None:
            raise ValueError("Курьер уже назначен")

        if not courier.is_available:
            raise ValueError("Курьер недоступен")

        self.__courier = courier
        courier.mark_busy()

    def calculate_total_price(self) -> float:
        items_price = sum(
            item.get_total_price()
            for item in self.__items
        )

        return (
            items_price
            + self.__delivery_method.calculate_cost()
        )

    def change_status(self, new_status: str) -> None:
        if new_status not in STATUS_FLOW[self.__status]:
            raise ValueError(
                f"Невозможно изменить статус "
                f"с {self.__status} на {new_status}"
            )

        if new_status == STATUS_IN_TRANSIT:
            if not self.__delivery_method.requires_courier:
                raise ValueError(
                    "Самовывоз нельзя перевести в статус «в пути»"
                )

            if self.__courier is None:
                raise ValueError("Сначала назначьте курьера")

        if (
            new_status == STATUS_READY_FOR_PICKUP
            and self.__delivery_method.requires_courier
        ):
            raise ValueError(
                "Этот статус доступен только для самовывоза"
            )

        self.__status = new_status

        if (
            new_status in [
                STATUS_DELIVERED,
                STATUS_COMPLETED,
                STATUS_CANCELLED,
            ]
            and self.__courier is not None
        ):
            self.__courier.mark_available()

    def change_delivery_method(
        self,
        new_method: DeliveryMethod,
    ) -> None:
        if self.__status not in [STATUS_CREATED, STATUS_CONFIRMED]:
            raise ValueError(
                "Изменить способ доставки можно "
                "только до отправки заказа"
            )

        if (
            self.__courier is not None
            and not new_method.requires_courier
        ):
            self.__courier.mark_available()
            self.__courier = None

        self.__delivery_method = new_method

    def check_items(self) -> None:
        if not self.__items:
            raise ValueError(
                "В заказе должна быть хотя бы одна позиция"
            )

        for item in self.__items:
            item.check_price()
            item.check_quantity()
