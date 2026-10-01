from client import Client
from constants import (
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    STATUS_DELIVERED,
    STATUS_IN_TRANSIT,
    STATUS_READY_FOR_PICKUP,
)
from couriers import Couriers
from delivery_methods import (
    DeliveryMethod,
    ExpressDelivery,
    PickupDelivery,
    StandardDelivery,
)
from order import Order
from order_item import OrderItem
from orders import Orders
from storage import Storage


class ConsoleApp:
    def __init__(
        self,
        orders: Orders,
        couriers: Couriers,
        storage: Storage,
    ):
        self.__orders = orders
        self.__couriers = couriers
        self.__storage = storage

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
            print("6. Добавить товар или изменить остаток на складе")
            print("7. Показать товары на складе")
            print("0. Выход")

            command = input("Выберите действие: ")

            match command:
                case "1":
                    self.create_order()

                case "2":
                    self.show_orders()

                case "3":
                    self.update_order_delivery()

                case "4":
                    self.assign_courier()

                case "5":
                    self.change_order_status()

                case "6":
                    self.add_storage_item()

                case "7":
                    self.__storage.show_items()

                case "0":
                    self.good_print("Работа завершена")
                    break
                case _:
                    self.good_print("Неверная команда")

    def show_available_items(
        self,
        selected_items: list[OrderItem] | None = None,
    ) -> None:
        stock_items = self.__storage.items
        for item in selected_items or []:
            stock_items[item.name.strip().lower()]["quantity"] -= item.quantity

        available_items = {
            name: item
            for name, item in stock_items.items()
            if item["quantity"] > 0
        }

        if not available_items:
            self.good_print("На складе нет доступных товаров")
            return

        print("\nДоступные товары на складе:")
        for name, item in available_items.items():
            print(
                f"{name} — {item['quantity']} шт., "
                f"{item['price']} руб. за шт."
            )

    def add_storage_item(self) -> None:
        print("\nДобавление товара или изменение остатка на складе")

        try:
            stock_items = self.__storage.items
            print("\nТовары на складе:")
            for name, item in stock_items.items():
                print(
                    f"{name} — {item['quantity']} шт., "
                    f"{item['price']} руб. за шт."
                )
            name = input("Введите название товара: ").strip().lower()
            if not name:
                raise ValueError("Название товара не может быть пустым")

            if name in stock_items:
                quantity = int(input("Введите новый остаток товара: "))
                self.__storage.set_quantity(name, quantity)
                self.good_print(f"Остаток товара {name}: {quantity} шт.")
            else:
                quantity = int(input("Введите количество нового товара: "))
                price = float(input("Введите цену нового товара: "))
                self.__storage.add_items(name, quantity, price)
                self.good_print(f"Товар {name} успешно добавлен на склад")

        except ValueError as e:
            self.good_print(
                f"Ошибка при изменении склада: {e}"
            )

    def read_positive_int(self, text: str, maximum: int | None = None) -> int:
        while True:
            try:
                value = int(input(text))
                if value <= 0:
                    raise ValueError("Введите положительное целое число")
                if maximum is not None and value > maximum:
                    raise ValueError(
                        f"Недостаточно товара на складе: доступно {maximum} шт."
                    )
                return value
            except ValueError as error:
                self.good_print(f"Ошибка: {error}")

    def read_required_text(self, text: str) -> str:
        while True:
            value = input(text).strip()
            if value:
                return value
            self.good_print("Поле не может быть пустым")

    def create_order(self) -> None:
        print("\nСоздание заказа")
        if not any(item["quantity"] > 0 for item in self.__storage.items.values()):
            self.good_print("На складе нет доступных товаров")
            return

        while True:
            order_id = self.read_positive_int("Введите ID заказа: ")
            if all(order.id != order_id for order in self.__orders.get_all_orders()):
                break
            self.good_print("Заказ с таким ID уже существует")

        client_id = self.read_positive_int("Введите ID клиента: ")
        client_name = self.read_required_text("Введите имя клиента: ")
        client_phone = self.read_required_text("Введите телефон клиента: ")
        client_address = self.read_required_text("Введите адрес клиента: ")
        client = Client(client_id, client_name, client_phone, client_address)
        items = []

        while True:
            self.show_available_items(items)
            item_name = input(
                "Введите название позиции (или '0' для завершения): "
            ).strip().lower()
            if item_name == "0":
                if items:
                    break
                self.good_print("В заказе должна быть хотя бы одна позиция")
                continue

            try:
                stock_item = self.__storage.get_current_item(item_name)
                selected_quantity = sum(
                    item.quantity for item in items if item.name == item_name
                )
                available_quantity = stock_item["quantity"] - selected_quantity
                if available_quantity <= 0:
                    raise ValueError("Товар отсутствует в доступном списке")
            except ValueError as error:
                self.good_print(f"Ошибка: {error}")
                continue

            item_quantity = self.read_positive_int(
                "Введите количество позиции: ", maximum=available_quantity
            )
            items.append(OrderItem(item_name, item_quantity, stock_item["price"]))

        print("\nВыберите способ доставки:")
        print("1. Стандартная доставка")
        print("2. Экспресс-доставка")
        print("3. Самовывоз")
        while True:
            delivery_choice = self.read_positive_int("Введите номер способа доставки: ")
            try:
                delivery_method = self.choose_delivery(delivery_choice)
                break
            except ValueError as error:
                self.good_print(f"Ошибка: {error}")

        order = Order(order_id, client, client_address, items, delivery_method)
        self.__orders.add_order(order)
        for item in order.items:
            self.__storage.take_items(item.name, item.quantity)
        self.good_print(f"Заказ с ID {order_id} успешно создан")

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
        match num:
            case 1:
                return StandardDelivery()
            case 2:
                return ExpressDelivery()
            case 3:
                return PickupDelivery()
            case _:
                raise ValueError("Неверный выбор доставки")

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

            courier.accept_order(order)

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
                f"({STATUS_CONFIRMED}, {STATUS_IN_TRANSIT}, "
                f"{STATUS_DELIVERED}, {STATUS_READY_FOR_PICKUP}, "
                f"{STATUS_COMPLETED}, {STATUS_CANCELLED}): "
            )

            order.change_status(
                new_status.strip().lower()
            )

            if order.status == STATUS_CANCELLED:
                for item in order.items:
                    self.__storage.return_items(item.name, item.quantity, item.price)

            self.good_print(
                "Статус успешно изменен!"
            )

            self.show_order(order)

        except ValueError as e:
            self.good_print(
                f"Ошибка при изменении статуса: {e}"
            )
