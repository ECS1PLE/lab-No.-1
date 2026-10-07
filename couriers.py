from collections.abc import Callable

from courier import Courier


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

    def add_couriers(
        self,
        id: int,
        new_courier: str | None = None,
        phone: str | None = None,
        *,
        good_print: Callable[[str], None],
    ) -> None:
        while True:
            if new_courier is None:
                new_courier = input("Введите имя курьера: ")
            new_courier = new_courier.strip()
            letters = new_courier.replace(" ", "").replace("-", "").replace("'", "")
            if not new_courier:
                good_print("Поле не может быть пустым. Введите имя заново.")
            elif letters.isalpha():
                break
            else:
                good_print(
                    "Имя курьера должно содержать буквы; допустимы пробелы, "
                    "дефисы и апострофы. Введите имя заново."
                )
            new_courier = None

        while True:
            if phone is None:
                phone = input("Введите телефон курьера: ")
            phone = phone.strip()
            digits = phone.removeprefix("+")
            if not phone:
                good_print("Поле не может быть пустым. Введите телефон заново.")
            elif digits.isascii() and digits.isdigit():
                break
            else:
                good_print(
                    "Телефон курьера должен содержать только цифры "
                    "и необязательный + в начале. Введите телефон заново."
                )
            phone = None

        courier = Courier(id, new_courier, phone)
        self.add_courier(courier)

    def show_couriers(self) -> None:
        if not self.__couriers:
            print("Список курьеров пуст.")
            return

        print("Список курьеров:")
        for courier in self.__couriers:
            availability = "Доступен" if courier.is_available else "Занят"
            print(f"ID: {courier.id}, Имя: {courier.name}, Телефон: {courier.phone}, Статус: {availability}")
