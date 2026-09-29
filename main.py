from abc import ABC, abstractmethod


class Client:
    def __init__(self, client_id: int, name: str, phone: str, address: str):
        if client_id <= 0:
            raise ValueError("ID клиента должен быть положительным")
        if not name.strip():
            raise ValueError("Имя клиента не может быть пустым")
        if not phone.strip():
            raise ValueError("Телефон клиента не может быть пустым")
        if not address.strip():
            raise ValueError("Адрес клиента не может быть пустым")

        self.__id = client_id
        self.__name = name.strip()
        self.__phone = phone.strip()
        self.__address = address.strip()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone(self) -> str:
        return self.__phone

    @property
    def address(self) -> str:
        return self.__address

    def change_address(self, new_address: str) -> None:
        if not new_address.strip():
            raise ValueError("Адрес клиента не может быть пустым")

        self.__address = new_address.strip()


class Courier:
    def __init__(self, courier_id: int, name: str, phone: str):
        if courier_id <= 0:
            raise ValueError("ID курьера должен быть положительным")
        if not name.strip():
            raise ValueError("Имя курьера не может быть пустым")
        if not phone.strip():
            raise ValueError("Телефон курьера не может быть пустым")

        self.__id = courier_id
        self.__name = name.strip()
        self.__phone = phone.strip()
        self.__is_available = True

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone(self) -> str:
        return self.__phone

    @property
    def is_available(self) -> bool:
        return self.__is_available

    def accept_order(self, order: "Order") -> None:
        order.assign_courier(self)

    def mark_busy(self) -> None:
        if not self.__is_available:
            raise ValueError("Курьер уже занят")

        self.__is_available = False

    def mark_available(self) -> None:
        self.__is_available = True


class Couriers:
    def __init__(self):
        self.__couriers: list[Courier] = []

    def add_courier(self, courier: Courier) -> None:
        for existing_courier in self.__couriers:
            if existing_courier.id == courier.id:
                raise ValueError("Курьер с таким ID уже существует")

        self.__couriers.append(courier)

    def get_available_couriers(self) -> list[Courier]:
        return [
            courier
            for courier in self.__couriers
            if courier.is_available
        ]

    def get_courier_by_id(self, courier_id: int) -> Courier:
        for courier in self.__couriers:
            if courier.id == courier_id:
                return courier
        raise ValueError("Курьер с таким ID не существует")

    def get_all_couriers(self) -> tuple[Courier, ...]:
        return tuple(self.__couriers)


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


class DeliveryMethod(ABC):
    requires_courier = True

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def calculate_cost(self) -> float:
        ...

    @abstractmethod
    def estimate_time(self) -> str:
        ...


class StandardDelivery(DeliveryMethod):
    @property
    def name(self) -> str:
        return "Стандартная доставка"

    def calculate_cost(self) -> float:
        return 350.0

    def estimate_time(self) -> str:
        return "Доставка через 3-5 дней"


class ExpressDelivery(DeliveryMethod):
    @property
    def name(self) -> str:
        return "Экспресс-доставка"

    def calculate_cost(self) -> float:
        return 500.0

    def estimate_time(self) -> str:
        return "Доставка через 1-2 дня"



class PickupDelivery(DeliveryMethod):
    requires_courier = False

    @property
    def name(self) -> str:
        return "Самовывоз"

    def calculate_cost(self) -> float:
        return 0.0

    def estimate_time(self) -> str:
        return "Готов через 30 минут"


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
        if not items:
            raise ValueError("В заказе должна быть хотя бы одна позиция")

        self.__id = order_id
        self.__client = client
        self.__address = address.strip()
        self.__items = list(items)
        self.__delivery_method = delivery_method
        self.__courier: Courier | None = None
        self.__status = "создан"

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
        if self.__status != "создан":
            raise ValueError(
                "Позиции можно добавлять только в созданный заказ"
            )

        if item.check_price() and item.check_quantity():
            self.__items.append(item)

    def assign_courier(self, courier: Courier) -> None:
        if self.__status not in ["создан", "подтвержден"]:
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
        status_flow = {
            "создан": [
                "подтвержден",
                "отменен",
            ],
            "подтвержден": [
                "в пути",
                "отменен",
                "готов к самовывозу",
            ],
            "в пути": [
                "доставлен",
                "отменен",
            ],
            "доставлен": [],
            "отменен": [],
            "готов к самовывозу": [
                "завершен",
                "отменен",
            ],
            "завершен": [],
        }

        if new_status not in status_flow[self.__status]:
            raise ValueError(
                f"Невозможно изменить статус "
                f"с {self.__status} на {new_status}"
            )

        if new_status == "в пути":
            if not self.__delivery_method.requires_courier:
                raise ValueError(
                    "Самовывоз нельзя перевести в статус «в пути»"
                )

            if self.__courier is None:
                raise ValueError("Сначала назначьте курьера")

        if (
            new_status == "готов к самовывозу"
            and self.__delivery_method.requires_courier
        ):
            raise ValueError(
                "Этот статус доступен только для самовывоза"
            )

        self.__status = new_status

        if (
            new_status in [
                "доставлен",
                "завершен",
                "отменен",
            ]
            and self.__courier is not None
        ):
            self.__courier.mark_available()

    def change_delivery_method(
        self,
        new_method: DeliveryMethod,
    ) -> None:
        if self.__status not in ["создан", "подтвержден"]:
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

    def change_delivery_method(self, new_method: DeliveryMethod) -> None:
        if self.status not in ["создан", "подтвержден"]:
            raise ValueError("Изменить способ доставки можно только до отправки заказа")

        if self.courier is not None and not new_method.requires_courier:
            self.courier.is_available = True
            self.courier = None
        self.delivery_method = new_method

    def check_items(self) -> None:
        if not self.__items:
            raise ValueError(
                "В заказе должна быть хотя бы одна позиция"
            )

        for item in self.__items:
            item.check_price()
            item.check_quantity()


class Orders:
    def __init__(self):
        self.__orders: list[Order] = []

    def add_order(self, order: Order) -> None:
        for existing_order in self.__orders:
            if existing_order.id == order.id:
                raise ValueError(
                    "Заказ с таким ID уже существует"
                )

        self.__orders.append(order)

    def get_order_by_id(self, order_id: int) -> Order:
        for order in self.__orders:
            if order.id == order_id:
                return order

        raise ValueError(
            "Заказ с таким ID не существует"
        )

    def get_all_orders(self) -> tuple[Order, ...]:
        return tuple(self.__orders)


class ConsoleApp:
    def __init__(
        self,
        orders: Orders,
        couriers: Couriers,
    ):
        self.__orders = orders
        self.__couriers = couriers

    @staticmethod
    def good_print(message: str) -> None:
        print("\n" + "-" * 30)
        print(message)
        print("-" * 30)

    def run(self) -> None:
        while True:
            print("\n1. Создать заказ")
            print("2. Показать заказы")
            print("3. Выбрать доставку")
            print("4. Назначить курьера")
            print("5. Изменить статус")
            print("0. Выход")

            command = input("Выберите действие: ")

            if command == "1":
                self.create_order()

            elif command == "2":
                self.show_orders()

            elif command == "3":
                self.update_order_delivery()

            elif command == "4":
                self.assign_courier()

            elif command == "5":
                self.change_order_status()

            elif command == "0":
                self.good_print("Работа завершена")
                break

            else:
                self.good_print("Такой команды нет")

    def create_order(self) -> None:
        print("\nСоздание заказа")

        try:
            order_id = int(
                input("Введите ID заказа: ")
            )

            client_id = int(
                input("Введите ID клиента: ")
            )

            client_name = input(
                "Введите имя клиента: "
            )

            client_phone = input(
                "Введите телефон клиента: "
            )

            client_address = input(
                "Введите адрес клиента: "
            )

            client = Client(
                client_id,
                client_name,
                client_phone,
                client_address,
            )

            items = []

            while True:
                item_name = input(
                    "Введите название позиции "
                    "(или '0' для завершения): "
                )

                if item_name == "0":
                    break

                item_quantity = int(
                    input(
                        "Введите количество позиции: "
                    )
                )

                item_price = float(
                    input(
                        "Введите цену позиции: "
                    )
                )

                item = OrderItem(
                    item_name,
                    item_quantity,
                    item_price,
                )

                items.append(item)

            print("\nВыберите способ доставки:")
            print("1. Стандартная доставка")
            print("2. Экспресс-доставка")
            print("3. Самовывоз")

            delivery_choice = int(
                input(
                    "Введите номер способа доставки: "
                )
            )

            delivery_method = self.choose_delivery(
                delivery_choice
            )

            order = Order(
                order_id,
                client,
                client_address,
                items,
                delivery_method,
            )

            self.__orders.add_order(order)

            self.good_print(
                f"Заказ с ID {order_id} успешно создан"
            )

        except ValueError as e:
            self.good_print(
                f"Ошибка при создании заказа: {e}"
            )

    def show_order(self, order: Order) -> None:
        if order.courier is not None:
            courier_name = order.courier.name
        else:
            courier_name = "Не назначен"

        items_str = ", ".join(
            (
                f"{item.name} "
                f"(x{item.quantity}, "
                f"{item.price} руб.)"
            )
            for item in order.items
        )

        info = (
            f"ID: {order.id}\n"
            f"Статус: {order.status}\n"
            f"Клиент: {order.client.name}\n"
            f"Телефон: {order.client.phone}\n"
            f"Адрес доставки: {order.address}\n"
            f"Позиции: {items_str}\n"
            f"Способ доставки: "
            f"{order.delivery_method.name}\n"
            f"Стоимость доставки: "
            f"{order.delivery_method.calculate_cost()} руб.\n"
            f"Срок: "
            f"{order.delivery_method.estimate_time()}\n"
            f"Курьер: {courier_name}\n"
            f"Итого: "
            f"{order.calculate_total_price()} руб."
        )

        self.good_print(info)

    def show_orders(self) -> None:
        orders = self.__orders.get_all_orders()

        if not orders:
            self.good_print("Заказов нет")
            return

        for order in orders:
            self.show_order(order)

    def choose_delivery(
        self,
        num: int,
    ) -> DeliveryMethod:
        if num == 1:
            return StandardDelivery()

        if num == 2:
            return ExpressDelivery()

        if num == 3:
            return PickupDelivery()

        raise ValueError(
            "Неверный выбор доставки"
        )

    def update_order_delivery(self) -> None:
        try:
            order_id = int(
                input("Введите ID заказа: ")
            )

            order = self.__orders.get_order_by_id(
                order_id
            )

            print(
                "\n1. Стандартная доставка\n"
                "2. Экспресс-доставка\n"
                "3. Самовывоз"
            )

            delivery_choice = int(
                input(
                    "Введите номер нового "
                    "способа доставки: "
                )
            )

            new_delivery = self.choose_delivery(
                delivery_choice
            )

            order.change_delivery_method(
                new_delivery
            )

            self.good_print(
                f"Способ доставки: "
                f"{new_delivery.name}\n"
                f"Стоимость доставки: "
                f"{new_delivery.calculate_cost()} руб.\n"
                f"Ориентировочный срок: "
                f"{new_delivery.estimate_time()}\n"
                f"Новая итоговая стоимость заказа: "
                f"{order.calculate_total_price()} руб."
            )

        except ValueError as e:
            self.good_print(
                f"Ошибка: {e}"
            )

    def update_order_delivery(self) -> None:

        try:
            order_id = int(input("Введите ID заказа: "))
            order = self.orders.get_order_by_id(order_id)

            print("\n1. Стандартная доставка\n2. Экспресс-доставка\n3. Самовывоз")
            delivery_choice = int(input("Введите номер нового способа доставки: "))
            new_delivery = self.choose_delivery(delivery_choice)

            order.change_delivery_method(new_delivery)

            self.good_print(f"Доставка обновлена. Ориентировочный срок: {new_delivery.estimate_time()}\n"
                            f"Новая итоговая стоимость заказа: {order.calculate_total_price()}")
        except ValueError as e:
            self.good_print(f"Ошибка: {e}")

    def assign_courier(self) -> None:
        try:
            order_id = int(
                input("Введите ID заказа: ")
            )

            order = self.__orders.get_order_by_id(
                order_id
            )

            available_couriers = (
                self.__couriers.get_available_couriers()
            )

            if not available_couriers:
                self.good_print(
                    "В данный момент нет доступных курьеров"
                )
                return

            print("\nДоступные курьеры:")

            for courier in available_couriers:
                print(
                    f"ID: {courier.id}, "
                    f"Имя: {courier.name}"
                )

            courier_id = int(
                input("Введите ID курьера: ")
            )

            courier = (
                self.__couriers.get_courier_by_id(
                    courier_id
                )
            )

            order.assign_courier(courier)

            self.good_print(
                f"Курьер {courier.name} "
                f"успешно назначен "
                f"на заказ {order.id}"
            )

        except ValueError as e:
            self.good_print(
                f"Ошибка: {e}"
            )

    def change_order_status(self) -> None:
        try:
            order_id = int(
                input("Введите ID заказа: ")
            )

            order = self.__orders.get_order_by_id(
                order_id
            )

            print(
                f"Текущий статус: {order.status}"
            )

            new_status = input(
                "Введите новый статус "
                "(подтвержден, в пути, доставлен, "
                "готов к самовывозу, завершен, "
                "отменен): "
            )

            order.change_status(
                new_status.lower()
            )

            self.good_print(
                "Статус успешно изменен!"
            )

            self.show_order(order)

        except ValueError as e:
            self.good_print(
                f"Ошибка при изменении статуса: {e}"
            )


def main() -> None:
    orders = Orders()
    couriers = Couriers()

    couriers.add_courier(
        Courier(
            1,
            "Иван",
            "+79990000001",
        )
    )

    couriers.add_courier(
        Courier(
            2,
            "Алексей",
            "+79990000002",
        )
    )

    app = ConsoleApp(
        orders,
        couriers,
    )

    app.run()


if __name__ == "__main__":
    main()
