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
