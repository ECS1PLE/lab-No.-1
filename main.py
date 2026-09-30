from console_app import ConsoleApp
from courier import Courier
from couriers import Couriers
from orders import Orders
from storage import Storage


def main() -> None:
    orders = Orders()
    couriers = Couriers()
    storage = Storage()

    storage.add_items("Клавиатура", 10, 2500)
    storage.add_items("Мышь", 15, 1200)
    storage.add_items("Роблокс", 5, 15000)

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
        storage,
    )

    app.run()


if __name__ == "__main__":
    main()
