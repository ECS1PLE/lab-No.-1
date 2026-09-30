from abc import ABC, abstractmethod


class DeliveryMethod(ABC):
    requires_courier = True

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def calculate_cost(self) -> float:
        ...

    @abstractmethod
    def estimate_time(self) -> str:
        ...


class StandardDelivery(DeliveryMethod):
    @property
    def name(self) -> str:
        return "Стандартная доставка"

    def calculate_cost(self) -> float:
        return 350.0

    def estimate_time(self) -> str:
        return "Доставка через 3-5 дней"


class ExpressDelivery(DeliveryMethod):
    @property
    def name(self) -> str:
        return "Экспресс-доставка"

    def calculate_cost(self) -> float:
        return 500.0

    def estimate_time(self) -> str:
        return "Доставка через 1-2 дня"


class PickupDelivery(DeliveryMethod):
    requires_courier = False

    @property
    def name(self) -> str:
        return "Самовывоз"

    def calculate_cost(self) -> float:
        return 0.0

    def estimate_time(self) -> str:
        return "Готов через 30 минут"
