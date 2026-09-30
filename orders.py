from order import Order


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
