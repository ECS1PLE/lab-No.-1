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
