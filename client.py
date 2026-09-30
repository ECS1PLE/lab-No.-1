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
