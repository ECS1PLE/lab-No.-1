import pytest

from delivery_methods import DeliveryMethod, ExpressDelivery, PickupDelivery, StandardDelivery


@pytest.mark.parametrize("delivery, name, cost, time, requires_courier", [
    (StandardDelivery, "Стандартная доставка", 350, "Доставка через 3-5 дней", True),
    (ExpressDelivery, "Экспресс-доставка", 500, "Доставка через 1-2 дня", True),
    (PickupDelivery, "Самовывоз", 0, "Готов через 30 минут", False),
])
def test_delivery_contract(delivery, name, cost, time, requires_courier):
    method = delivery()
    assert isinstance(method, DeliveryMethod)
    assert method.name == name
    assert method.calculate_cost() == cost
    assert method.estimate_time() == time
    assert method.requires_courier is requires_courier


def test_abstract_delivery_cannot_be_created():
    with pytest.raises(TypeError):
        DeliveryMethod()
