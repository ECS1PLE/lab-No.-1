from types import SimpleNamespace

import pytest

from client import Client
from console_app import ConsoleApp
from courier import Courier
from couriers import Couriers
from delivery_methods import StandardDelivery
from order import Order
from order_item import OrderItem
from orders import Orders
from storage import Storage


@pytest.fixture
def client():
    return Client(1, "Анна", "+79990000000", "Невский, 1")


@pytest.fixture
def courier():
    return Courier(1, "Иван", "+79990000001")


@pytest.fixture
def make_order(client):
    def create(order_id=1, delivery=None):
        return Order(order_id, client, client.address,
                     [OrderItem("мышь", 2, 1200)], delivery or StandardDelivery())
    return create


@pytest.fixture
def order(make_order):
    return make_order()


@pytest.fixture
def storage():
    result = Storage()
    result.add_items("мышь", 5, 1200)
    return result


@pytest.fixture
def app_env(storage, courier):
    orders = Orders()
    couriers = Couriers()
    couriers.add_courier(courier)
    return SimpleNamespace(
        app=ConsoleApp(orders, couriers, storage), orders=orders,
        couriers=couriers, storage=storage, courier=courier,
    )


@pytest.fixture
def interact(monkeypatch, capsys):
    """Запустить действие с вводом и проверить, что все ответы использованы."""
    def run(action, answers):
        pending = iter(answers)
        with monkeypatch.context() as patch:
            patch.setattr("builtins.input", lambda prompt: next(pending))
            result = action()
        assert list(pending) == [], "Не все ожидаемые ответы были запрошены"
        return result, capsys.readouterr().out
    return run
