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
        for order in self.__orders:
            if order.id == order_id:
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
    def __init__(self, orders: Orders):
        self.orders = orders

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
                self.choose_delivery()
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
        pass

    def show_orders(self) -> None:
        if not self.orders.get_all_orders():
            self.good_print("Заказов нет")
            return
        for order in self.orders.get_all_orders():
            self.good_print(f"ID: {order.id}, Статус: {order.status}, Итого: {order.calculate_total_price()}")

    def choose_delivery(self) -> None:
        pass

    def assign_courier(self) -> None:
        pass

    def change_order_status(self) -> None:
        pass

orders = Orders()
app = ConsoleApp(orders)
app.run()