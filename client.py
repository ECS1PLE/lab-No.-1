from collections.abc import Callable


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

    @staticmethod
    def read_name(good_print: Callable[[str], None]) -> str:
        while True:
            name = input("Введите имя клиента: ").strip()
            letters = name.replace(" ", "").replace("-", "").replace("'", "")
            if not name:
                good_print("Поле не может быть пустым. Введите имя заново.")
            elif letters.isalpha():
                return name
            else:
                good_print(
                    "Имя клиента должно содержать буквы; допустимы пробелы, "
                    "дефисы и апострофы. Введите имя заново."
                )

    @staticmethod
    def read_phone(good_print: Callable[[str], None]) -> str:
        while True:
            phone = input("Введите телефон клиента: ").strip()
            digits = phone.removeprefix("+")
            if not phone:
                good_print("Поле не может быть пустым. Введите телефон заново.")
            elif digits.isascii() and digits.isdigit():
                return phone
            else:
                good_print(
                    "Телефон клиента должен содержать только цифры "
                    "и необязательный + в начале. Введите телефон заново."
                )

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
