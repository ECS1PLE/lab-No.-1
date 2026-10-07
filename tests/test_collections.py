import pytest

from courier import Courier
from couriers import Couriers
from orders import Orders


def test_orders_add_lookup_and_snapshot(make_order):
    orders = Orders()
    assert orders.get_all_orders() == ()
    first, second = make_order(1), make_order(2)
    orders.add_order(first)
    snapshot = orders.get_all_orders()
    orders.add_order(second)
    assert orders.get_order_by_id(1) is first
    assert orders.get_order_by_id(2) is second
    assert orders.get_all_orders() == (first, second)
    assert snapshot == (first,)
    with pytest.raises(ValueError, match="уже существует"):
        orders.add_order(make_order(1))
    assert orders.get_all_orders() == (first, second)


@pytest.mark.parametrize("populated", [False, True])
def test_missing_order(populated, order):
    orders = Orders()
    if populated:
        orders.add_order(order)
    with pytest.raises(ValueError, match="не существует"):
        orders.get_order_by_id(99)


def test_couriers_add_lookup_availability_and_snapshot(courier):
    couriers = Couriers()
    assert couriers.get_all_couriers() == ()
    assert couriers.get_available_couriers() == []
    couriers.add_courier(courier)
    snapshot = couriers.get_all_couriers()
    second = Courier(2, "Петр", "456")
    couriers.add_courier(second)
    assert couriers.get_courier_by_id(1) is courier
    assert couriers.get_courier_by_id(2) is second
    assert snapshot == (courier,)
    courier.mark_busy()
    assert couriers.get_available_couriers() == [second]
    second.mark_busy()
    assert couriers.get_available_couriers() == []
    courier.mark_available()
    assert couriers.get_available_couriers() == [courier]
    with pytest.raises(ValueError, match="уже существует"):
        couriers.add_courier(Courier(1, "Другой", "789"))
    assert couriers.get_all_couriers() == (courier, second)


@pytest.mark.parametrize("populated", [False, True])
def test_missing_courier(populated, courier):
    couriers = Couriers()
    if populated:
        couriers.add_courier(courier)
    with pytest.raises(ValueError, match="не существует"):
        couriers.get_courier_by_id(99)


def test_add_courier_from_fields_rejects_busy_duplicate(courier):
    couriers = Couriers()
    couriers.add_courier(courier)
    courier.mark_busy()
    with pytest.raises(ValueError, match="уже существует"):
        couriers.add_couriers(1, "Петр", "456", good_print=print)
    assert couriers.get_all_couriers() == (courier,)
    assert not courier.is_available


@pytest.mark.parametrize("args", [
    (0, "Петр", "456"), (-1, "Петр", "456"),
])
def test_add_courier_from_invalid_fields_keeps_collection(args):
    couriers = Couriers()
    with pytest.raises(ValueError):
        couriers.add_couriers(*args, good_print=print)
    assert couriers.get_all_couriers() == ()


@pytest.mark.parametrize("name, phone, answers", [
    (" \t", "456", ["Петр"]),
    ("Петр123", "456", ["Петр"]),
    ("Петр", " \t", ["456"]),
    ("Петр", "abc", ["456"]),
])
def test_add_couriers_validates_supplied_fields_and_retries(interact, name, phone, answers):
    couriers = Couriers()
    messages = []
    interact(lambda: couriers.add_couriers(2, name, phone, good_print=messages.append), answers)
    assert len(messages) == 1
    assert "заново" in messages[0]
    courier = couriers.get_courier_by_id(2)
    assert (courier.name, courier.phone) == ("Петр", "456")
