import pytest
from client import Client
from constants import (
    STATUS_CANCELLED, STATUS_COMPLETED, STATUS_CONFIRMED,
    STATUS_DELIVERED, STATUS_IN_TRANSIT, STATUS_READY_FOR_PICKUP,
)
from delivery_methods import ExpressDelivery, PickupDelivery, StandardDelivery
from order import Order


class TestOrderWorkflows:

    @pytest.fixture(autouse=True)
    def setup(self, app_env, interact):
        self.storage = app_env.storage
        self.orders = app_env.orders
        self.courier = app_env.courier
        self.app = app_env.app
        self.interact = lambda action, answers: interact(action, answers)[1]

    def create_order(self, delivery='1'):
        self.interact(self.app.create_order, [
            '1', '1', 'Анна', '+79990000000', 'Невский, 1',
            'мышь', '2', 'мышь', '1', '0', delivery,
        ])
        return self.orders.get_order_by_id(1)

    def change_status(self, status):
        return self.interact(self.app.change_order_status, ['1', status])

    def test_invalid_fields_retry_without_losing_order(self):
        self.interact(self.app.create_order, [
            'abc', '0', '1', '-1', 'x', '1',
            ' ', 'Анна', '', '+79990000000', '', 'Невский, 1',
            '0', 'нет такого товара', 'мышь', 'x', '0', '-2', '6', '2',
            'мышь', '4', '3', 'мышь', '0', 'x', '9', '3',
        ])
        order = self.orders.get_order_by_id(1)
        assert [item.quantity for item in order.items] == [2, 3]
        assert order.client.name == 'Анна'
        assert isinstance(order.delivery_method, PickupDelivery)
        assert self.storage.get_current_item('мышь')['quantity'] == 0

    def test_duplicate_id_retries_only_id(self):
        self.create_order()
        self.interact(self.app.create_order, ['1', '2', '2', 'Петр', '123', 'Адрес', 'мышь', '1', '0', '1'])
        assert len(self.orders.get_all_orders()) == 2
        assert self.storage.get_current_item('мышь')['quantity'] == 1

    def test_empty_stock_does_not_prompt(self):
        self.storage.set_quantity('мышь', 0)
        self.interact(self.app.create_order, [])
        assert self.orders.get_all_orders() == ()

    def test_cancel_returns_items_and_courier_once(self):
        order = self.create_order()
        self.interact(self.app.assign_courier, ['1', '1'])
        assert not self.courier.is_available
        assert self.storage.get_current_item('мышь')['quantity'] == 2
        self.change_status(' ОТМЕНЕН ')
        assert order.status == STATUS_CANCELLED
        assert self.courier.is_available
        assert self.storage.get_current_item('мышь')['quantity'] == 5
        assert len(order.items) == 2
        output = self.change_status(STATUS_CANCELLED)
        assert 'Невозможно изменить статус' in output
        assert self.storage.get_current_item('мышь')['quantity'] == 5

    def test_cancel_in_transit(self):
        self.create_order()
        self.interact(self.app.assign_courier, ['1', '1'])
        self.change_status(STATUS_CONFIRMED)
        self.change_status(STATUS_IN_TRANSIT)
        self.change_status(STATUS_CANCELLED)
        assert self.courier.is_available
        assert self.storage.get_current_item('мышь')['quantity'] == 5

    def test_cancel_pickup(self):
        self.create_order('3')
        self.change_status(STATUS_CONFIRMED)
        self.change_status(STATUS_READY_FOR_PICKUP)
        self.change_status(STATUS_CANCELLED)
        assert self.storage.get_current_item('мышь')['quantity'] == 5

    def test_return_preserves_current_price(self):
        self.create_order()
        self.storage.add_items('мышь', 1, 1500)
        self.change_status(STATUS_CANCELLED)
        assert self.storage.get_current_item('мышь') == {'quantity': 6, 'price': 1500}

    def test_return_restores_removed_product(self):
        self.create_order()
        self.storage.remove_items('мышь')
        self.change_status(STATUS_CANCELLED)
        assert self.storage.get_current_item('мышь') == {'quantity': 3, 'price': 1200}

    def test_delivered_order_does_not_return_stock(self):
        order = self.create_order()
        self.interact(self.app.assign_courier, ['1', '1'])
        self.change_status(STATUS_CONFIRMED)
        self.change_status(STATUS_IN_TRANSIT)
        self.change_status(STATUS_DELIVERED)
        self.change_status(STATUS_CANCELLED)
        assert order.status == STATUS_DELIVERED
        assert self.courier.is_available
        assert self.storage.get_current_item('мышь')['quantity'] == 2

    def test_completed_pickup_does_not_return_stock(self):
        order = self.create_order('3')
        self.change_status(STATUS_CONFIRMED)
        self.change_status(STATUS_READY_FOR_PICKUP)
        self.change_status(STATUS_COMPLETED)
        self.change_status(STATUS_CANCELLED)
        assert order.status == STATUS_COMPLETED
        assert self.storage.get_current_item('мышь')['quantity'] == 2

    def test_empty_order_rejected(self):
        with pytest.raises(ValueError, match='хотя бы одна позиция'):
            Order(1, Client(1, 'Анна', '123', 'Адрес'), 'Адрес', [], PickupDelivery())

    def test_delivery_choices(self):
        for number, delivery in [(1, StandardDelivery), (2, ExpressDelivery), (3, PickupDelivery)]:
            assert isinstance(self.app.choose_delivery(number), delivery)
        with pytest.raises(ValueError):
            self.app.choose_delivery(4)

    def test_menu_invalid_command_and_exit(self):
        output = self.interact(self.app.run, ['unknown', '0'])
        assert 'Неверная команда' in output
        assert 'Работа завершена' in output
