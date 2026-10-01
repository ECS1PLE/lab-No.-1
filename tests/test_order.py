import pytest

from constants import (
    STATUS_CANCELLED, STATUS_COMPLETED, STATUS_CONFIRMED, STATUS_CREATED,
    STATUS_DELIVERED, STATUS_IN_TRANSIT, STATUS_READY_FOR_PICKUP,
)
from courier import Courier
from delivery_methods import ExpressDelivery, PickupDelivery, StandardDelivery
from order import Order
from order_item import OrderItem


# Ожидаемые переходы заданы независимо от STATUS_FLOW приложения.
PATHS = {
    STATUS_CREATED: [],
    STATUS_CONFIRMED: [STATUS_CONFIRMED],
    STATUS_IN_TRANSIT: [STATUS_CONFIRMED, STATUS_IN_TRANSIT],
    STATUS_DELIVERED: [STATUS_CONFIRMED, STATUS_IN_TRANSIT, STATUS_DELIVERED],
    STATUS_READY_FOR_PICKUP: [STATUS_CONFIRMED, STATUS_READY_FOR_PICKUP],
    STATUS_COMPLETED: [STATUS_CONFIRMED, STATUS_READY_FOR_PICKUP, STATUS_COMPLETED],
    STATUS_CANCELLED: [STATUS_CANCELLED],
}
ALLOWED = {
    STATUS_CREATED: {STATUS_CONFIRMED, STATUS_CANCELLED},
    STATUS_CONFIRMED: {STATUS_IN_TRANSIT, STATUS_READY_FOR_PICKUP, STATUS_CANCELLED},
    STATUS_IN_TRANSIT: {STATUS_DELIVERED, STATUS_CANCELLED},
    STATUS_READY_FOR_PICKUP: {STATUS_COMPLETED, STATUS_CANCELLED},
    STATUS_COMPLETED: set(), STATUS_DELIVERED: set(), STATUS_CANCELLED: set(),
}


def advance(order, status):
    for step in PATHS[status]:
        order.change_status(step)


def test_order_properties_and_item_list_copy(client):
    item = OrderItem("мышь", 2, 1200)
    items = [item]
    delivery = StandardDelivery()
    order = Order(3, client, " Адрес ", items, delivery)
    items.clear()
    assert (order.id, order.client, order.address) == (3, client, "Адрес")
    assert order.items == (item,)
    assert order.delivery_method is delivery
    assert order.courier is None
    assert order.status == STATUS_CREATED
    assert order.check_items() is None


@pytest.mark.parametrize("order_id, address, empty", [
    (0, "Адрес", False), (-1, "Адрес", False),
    (1, " ", False), (1, "Адрес", True),
])
def test_invalid_order(client, order_id, address, empty):
    with pytest.raises(ValueError):
        Order(order_id, client, address,
              [] if empty else [OrderItem("мышь", 1, 1200)], StandardDelivery())


@pytest.mark.parametrize("delivery, expected", [
    (StandardDelivery, 2750), (ExpressDelivery, 2900), (PickupDelivery, 2400),
])
def test_total_and_add_item(make_order, delivery, expected):
    order = make_order(delivery=delivery())
    assert order.calculate_total_price() == expected
    item = OrderItem("клавиатура", 2, 2500)
    order.add_item(item)
    assert order.items[-1] is item
    assert order.calculate_total_price() == expected + 5000


@pytest.mark.parametrize("status", list(PATHS)[1:])
def test_cannot_add_items_after_creation(make_order, courier, status):
    pickup = status in (STATUS_READY_FOR_PICKUP, STATUS_COMPLETED)
    order = make_order(delivery=PickupDelivery() if pickup else StandardDelivery())
    if not pickup:
        courier.accept_order(order)
    advance(order, status)
    previous = order.items
    with pytest.raises(ValueError, match="только в созданный"):
        order.add_item(OrderItem("новый", 1, 1))
    assert order.items == previous


@pytest.mark.parametrize("status", [STATUS_CREATED, STATUS_CONFIRMED])
def test_assign_before_dispatch(order, courier, status):
    advance(order, status)
    order.assign_courier(courier)
    assert order.courier is courier
    assert not courier.is_available


@pytest.mark.parametrize("reason", ["pickup", "busy", "assigned", "cancelled"])
def test_invalid_assignment_keeps_state(make_order, courier, reason):
    order = make_order(delivery=PickupDelivery() if reason == "pickup" else StandardDelivery())
    if reason == "busy":
        courier.mark_busy()
    if reason == "assigned":
        order.assign_courier(Courier(2, "Петр", "456"))
    if reason == "cancelled":
        order.change_status(STATUS_CANCELLED)
    previous, available = order.courier, courier.is_available
    with pytest.raises(ValueError):
        order.assign_courier(courier)
    assert order.courier is previous
    assert courier.is_available is available


@pytest.mark.parametrize("pickup, source", [
    (False, STATUS_CREATED), (False, STATUS_CONFIRMED),
    (False, STATUS_IN_TRANSIT), (False, STATUS_DELIVERED), (False, STATUS_CANCELLED),
    (True, STATUS_CREATED), (True, STATUS_CONFIRMED),
    (True, STATUS_READY_FOR_PICKUP), (True, STATUS_COMPLETED), (True, STATUS_CANCELLED),
])
@pytest.mark.parametrize("target", [*PATHS, "неизвестный"])
def test_status_transition_matrix(make_order, courier, pickup, source, target):
    order = make_order(delivery=PickupDelivery() if pickup else StandardDelivery())
    if not pickup:
        order.assign_courier(courier)
    advance(order, source)
    available = courier.is_available
    allowed = target in ALLOWED[source]
    allowed = allowed and not (pickup and target == STATUS_IN_TRANSIT)
    allowed = allowed and not (not pickup and target == STATUS_READY_FOR_PICKUP)
    if allowed:
        order.change_status(target)
        assert order.status == target
        assert courier.is_available is (
            pickup or target in (STATUS_CANCELLED, STATUS_DELIVERED, STATUS_COMPLETED)
        )
    else:
        with pytest.raises(ValueError):
            order.change_status(target)
        assert order.status == source
        assert courier.is_available is available


def test_dispatch_requires_courier(order):
    order.change_status(STATUS_CONFIRMED)
    with pytest.raises(ValueError, match="Сначала назначьте курьера"):
        order.change_status(STATUS_IN_TRANSIT)
    assert order.status == STATUS_CONFIRMED


@pytest.mark.parametrize("status", [STATUS_CREATED, STATUS_CONFIRMED])
@pytest.mark.parametrize("pickup", [False, True])
def test_change_delivery_updates_cost_and_courier(order, courier, status, pickup):
    order.assign_courier(courier)
    advance(order, status)
    method = PickupDelivery() if pickup else ExpressDelivery()
    order.change_delivery_method(method)
    assert order.delivery_method is method
    assert order.calculate_total_price() == (2400 if pickup else 2900)
    assert order.courier is (None if pickup else courier)
    assert courier.is_available is pickup


@pytest.mark.parametrize("status", list(PATHS)[2:])
def test_cannot_change_delivery_after_dispatch_or_cancellation(make_order, courier, status):
    pickup = status in (STATUS_READY_FOR_PICKUP, STATUS_COMPLETED)
    order = make_order(delivery=PickupDelivery() if pickup else StandardDelivery())
    if not pickup:
        order.assign_courier(courier)
    advance(order, status)
    previous, available = order.delivery_method, courier.is_available
    with pytest.raises(ValueError, match="только до отправки"):
        order.change_delivery_method(ExpressDelivery())
    assert order.delivery_method is previous
    assert courier.is_available is available
