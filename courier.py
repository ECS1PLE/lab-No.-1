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

    def accept_order(self, order) -> None:
        order.assign_courier(self)

    def mark_busy(self) -> None:
        if not self.__is_available:
            raise ValueError("Курьер уже занят")

        self.__is_available = False

    def mark_available(self) -> None:
        self.__is_available = True
