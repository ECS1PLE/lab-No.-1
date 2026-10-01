import pytest

from client import Client
from courier import Courier
from order_item import OrderItem


@pytest.mark.parametrize("args", [
    (0, "Анна", "123", "Адрес"), (-1, "Анна", "123", "Адрес"),
    (1, " ", "123", "Адрес"), (1, "Анна", "", "Адрес"),
    (1, "Анна", "123", "\t"),
])
def test_client_rejects_invalid_fields(args):
    with pytest.raises(ValueError):
        Client(*args)


def test_client_properties_and_address_change():
    client = Client(3, " Анна ", " 123 ", " Адрес ")
    assert (client.id, client.name, client.phone, client.address) == (3, "Анна", "123", "Адрес")
    client.change_address(" Новый адрес ")
    assert client.address == "Новый адрес"


@pytest.mark.parametrize("address", ["", " ", "\n\t"])
def test_invalid_address_does_not_change_client(client, address):
    previous = client.address
    with pytest.raises(ValueError):
        client.change_address(address)
    assert client.address == previous


@pytest.mark.parametrize("args", [
    (0, "Иван", "123"), (-1, "Иван", "123"),
    (1, " ", "123"), (1, "Иван", ""),
])
def test_courier_rejects_invalid_fields(args):
    with pytest.raises(ValueError):
        Courier(*args)


def test_courier_properties():
    courier = Courier(2, " Иван ", " 123 ")
    assert (courier.id, courier.name, courier.phone) == (2, "Иван", "123")
    assert courier.is_available


def test_courier_busy_and_available(courier):
    courier.mark_busy()
    assert not courier.is_available
    with pytest.raises(ValueError, match="уже занят"):
        courier.mark_busy()
    assert not courier.is_available
    courier.mark_available()
    courier.mark_available()
    assert courier.is_available


def test_accept_order_assigns_courier(courier, order):
    courier.accept_order(order)
    assert order.courier is courier
    assert not courier.is_available


@pytest.mark.parametrize("args", [
    ("", 1, 10), (" \t", 1, 10), ("мышь", 0, 10),
    ("мышь", -1, 10), ("мышь", 1, -0.01),
])
def test_item_rejects_invalid_fields(args):
    with pytest.raises(ValueError):
        OrderItem(*args)


@pytest.mark.parametrize("quantity, price, total", [(1, 0, 0), (3, 2.5, 7.5), (2, 1200, 2400)])
def test_item_properties_validation_and_total(quantity, price, total):
    item = OrderItem(" мышь ", quantity, price)
    assert (item.name, item.quantity, item.price) == ("мышь", quantity, price)
    assert item.get_total_price() == pytest.approx(total)
    assert item.check_price() is True
    assert item.check_quantity() is True
