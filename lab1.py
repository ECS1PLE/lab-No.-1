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
        order.assign_courier(self)


class Couriers:
    def __init__(self):
        self.__couriers: list[Courier] = []

    def add_courier(self, courier: Courier) -> None:
        courier_id = courier.id
        for existing_courier in self.__couriers:
            if existing_courier.id == courier_id:
                raise ValueError("Курьер с таким ID уже существует")
        self.__couriers.append(courier)

    def get_available_couriers(self) -> list[Courier]:
        return [courier for courier in self.__couriers if courier.is_available]

    def get_courier_by_id(self, courier_id: int) -> Courier:
        for courier in self.__couriers:
            if courier.id == courier_id:
                return courier

        raise ValueError("Курьер с таким ID не существует")


class OrderItem:
    def __init__(self, name: str, quantity: int, price: float):
        self.name = name
        self.quantity = quantity
        self.price = price

    def get_total_price(self) -> float:
        return self.quantity * self.price

    def check_price(self) -> bool:
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        return True

    def check_quantity(self) -> bool:
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        return True


class DeliveryMethod(ABC):
    requires_courier = True

    @abstractmethod
    def calculate_cost(self) -> float:
        ...

    @abstractmethod
    def estimate_time(self) -> str:
        ...


class StandartDelivery(DeliveryMethod):
    def calculate_cost(self) -> float:
        return 350.0

    def estimate_time(self) -> str:
        return "Доставка через 3-5 дней"


class ExpressDelivery(DeliveryMethod):
    def calculate_cost(self) -> float:
        return 500.0

    def estimate_time(self) -> str:
        return "Доставчка через 1-2 дня"


class PickupDelivery(DeliveryMethod):
    requires_courier = False

    def calculate_cost(self) -> float:
        return 0.0

    def estimate_time(self) -> str:
        return "Готов через 30 минут"


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
        self.check_items()

    def add_item(self, item: OrderItem) -> None:
        if self.status != "создан":
            raise ValueError("Позиции можно добавлять только в созданный заказ")
        if item.check_price() and item.check_quantity():
            self.items.append(item)

    def assign_courier(self, courier: Courier) -> None:
        if self.status != "создан":
            raise ValueError("Курьера можно назначить только для созданного заказа")

        if not self.delivery_method.requires_courier:
            raise ValueError("Самовывоз не требует курьера")

        if self.courier is not None:
            raise ValueError("Курьер уже назначен")

        if not courier.is_available:
            raise ValueError("Курьер недоступен")

        self.courier = courier
        courier.is_available = False

    def calculate_total_price(self) -> float:
        items_price = sum(item.get_total_price() for item in self.items)
        return items_price + self.delivery_method.calculate_cost()

    def change_status(self, new_status: str) -> None:
        status_flow = {
            "создан": ["подтвержден", "отменен"],
            "подтвержден": ["в пути", "отменен", "готов к самовывозу"],
            "в пути": ["доставлен", "отменен"],
            "доставлен": [],
            "отменен": [],
            "готов к самовывозу": ["завершен", "отменен"],
            "завершен": [],
        }
        if new_status not in status_flow[self.status]:
            raise ValueError(f"Невозможно изменить статус с {self.status} на {new_status}")
        if new_status == "в пути":
            if not self.delivery_method.requires_courier:
                raise ValueError("Самовывоз нельзя перевести в статус «в пути»")
            if self.courier is None:
                raise ValueError("Сначала назначьте курьера")

        if new_status == "готов к самовывозу" and self.delivery_method.requires_courier:
            raise ValueError("Этот статус доступен только для самовывоза")

        self.status = new_status

        if new_status in ["доставлен", "завершен", "отменен"] and self.courier is not None:
            self.courier.is_available = True

    def change_delivery_method(self, new_method: DeliveryMethod) -> None:
        if self.status not in ["создан", "подтвержден"]:
            raise ValueError("Изменить способ доставки можно только до отправки заказа")

        if self.courier is not None and not new_method.requires_courier:
            self.courier.is_available = True
            self.courier = None
        self.delivery_method = new_method

    def check_items(self) -> None:
        if not self.items:
            raise ValueError("В заказе должна быть хотя бы одна позиция")

        for item in self.items:
            item.check_price()
            item.check_quantity()


class Orders:
    def __init__(self):
        self.__orders: list[Order] = []

    def add_order(self, order: Order) -> None:
        order_id = order.id
        for existing_order in self.__orders:
            if existing_order.id == order_id:
                raise ValueError("Заказ с таким ID уже существует")
        self.__orders.append(order)

    def get_order_by_id(self, order_id: int) -> Order:
        for order in self.__orders:
            if order.id == order_id:
                return order

        raise ValueError("Заказ с таким ID не существует")

    def get_all_orders(self) -> list[Order]:
        return self.__orders.copy()


class ConsoleApp:
    def __init__(self, orders: Orders, couriers: Couriers):
        self.orders = orders
        self.couriers = couriers

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
            order_id = int(input("Введите ID заказа: "))
            client_id = int(input("Введите ID клиента: "))
            client_name = input("Введите имя клиента: ")
            client_phone = input("Введите телефон клиента: ")
            client_address = input("Введите адрес клиента: ")
            client = Client(client_id, client_name, client_phone, client_address)

            items = []
            while True:
                item_name = input("Введите название позиции (или '0' для завершения): ")
                if item_name == "0":
                    break
                item_quantity = int(input("Введите количество позиции: "))
                item_price = float(input("Введите цену позиции: "))
                item = OrderItem(item_name, item_quantity, item_price)
                items.append(item)

            print("\nВыберите способ доставки:")
            print("1. Стандартная доставка")
            print("2. Экспресс-доставка")
            print("3. Самовывоз")
            delivery_choice = int(input("Введите номер способа доставки: "))
            delivery_method = self.choose_delivery(num=delivery_choice)

            order = Order(order_id, client, client_address, items, delivery_method)
            self.orders.add_order(order)
            self.good_print(f"Заказ с ID {order_id} успешно создан")
        except ValueError as e:
            self.good_print(f"Ошибка при создании заказа: {e}")

    def show_orders(self) -> None:
        orders = self.orders.get_all_orders()
        if not orders:
            self.good_print("Заказов нет")
            return

        for order in orders:
            courier_name = order.courier.name if order.courier else "Не назначен"
            items_str = ', '.join([f'{item.name} (x{item.quantity})' for item in order.items])

            info = (f"ID: {order.id} | Статус: {order.status} | Адрес: {order.address}\n"
                    f"Имя заказчика: {order.client.name} | Телефон: {order.client.phone}\n"
                    f"Элементы: {items_str} \n"
                    f"Доставка: {order.delivery_method.estimate_time()} | Курьер: {courier_name} | Адрес: {order.client.address}\n"
                    f"Итого: {order.calculate_total_price()} руб.")
            self.good_print(info)

    def choose_delivery(self, num: int) -> DeliveryMethod:
        if num == 1:
            return StandartDelivery()
        elif num == 2:
            return ExpressDelivery()
        elif num == 3:
            return PickupDelivery()
        else:
            raise ValueError("Неверный выбор доставки")

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
            order_id = int(input("Введите ID заказа: "))
            order = self.orders.get_order_by_id(order_id)

            available_couriers = self.couriers.get_available_couriers()
            if not available_couriers:
                self.good_print("В данный момент нет доступных курьеров")
                return

            print("\nДоступные курьеры:")
            for c in available_couriers:
                print(f"ID: {c.id}, Имя: {c.name}")

            courier_id = int(input("Введите ID курьера: "))
            courier = self.couriers.get_courier_by_id(courier_id)

            order.assign_courier(courier)
            self.good_print(f"Курьер {courier.name} успешно назначен на заказ {order.id}")
        except ValueError as e:
            self.good_print(f"Ошибка: {e}")

    def change_order_status(self) -> None:
        try:
            order_id = int(input("Введите ID заказа: "))
            order = self.orders.get_order_by_id(order_id)

            print(f"Текущий статус: {order.status}")
            new_status = input(
                "Введите новый статус (подтвержден, в пути, доставлен, готов к самовывозу, завершен, отменен): ")

            order.change_status(new_status.lower())

            courier_info = f", Курьер: {order.courier.name}" if order.courier else ", Курьер: не назначен"
            self.good_print(f"Статус успешно изменен!\nЗаказ {order.id}: {order.status}{courier_info}")
        except ValueError as e:
            self.good_print(f"Ошибка при изменении статуса: {e}")


orders = Orders()

couriers = Couriers()
couriers.add_courier(
    Courier(1, "Иван", "+79990000001")
)
couriers.add_courier(
    Courier(2, "Алексей", "+79990000002")
)

app = ConsoleApp(orders, couriers)
app.run()