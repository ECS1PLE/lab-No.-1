import pytest

from console_app import ConsoleApp
from constants import STATUS_CREATED
from delivery_methods import ExpressDelivery, PickupDelivery, StandardDelivery
from order_item import OrderItem


def test_good_print(capsys):
    ConsoleApp.good_print("Сообщение")
    assert capsys.readouterr().out == "\n" + "-" * 30 + "\nСообщение\n" + "-" * 30 + "\n"


@pytest.mark.parametrize("bad", ["abc", "", "1.5", "0", "-2", "4"])
def test_integer_input_retries_current_field(app_env, interact, bad):
    result, output = interact(lambda: app_env.app.read_positive_int("Количество: ", 3), [bad, "3"])
    assert result == 3
    assert "Ошибка:" in output


def test_integer_input_without_limit(app_env, interact):
    result, _ = interact(lambda: app_env.app.read_positive_int("ID: "), [" 1000000 "])
    assert result == 1000000


def test_required_text_retries_and_trims(app_env, interact):
    result, output = interact(lambda: app_env.app.read_required_text("Имя: "), ["", "\t", " Анна "])
    assert result == "Анна"
    assert output.count("Поле не может быть пустым") == 2


@pytest.mark.parametrize("selected, remaining", [(0, 5), (2, 3), (5, 0)])
def test_available_items_does_not_mutate_stock(app_env, capsys, selected, remaining):
    items = [OrderItem("мышь", selected, 1200)] if selected else None
    app_env.app.show_available_items(items)
    output = capsys.readouterr().out
    if remaining:
        assert f"мышь — {remaining} шт., 1200 руб." in output
    else:
        assert "нет доступных товаров" in output
    assert app_env.storage.get_current_item("мышь")["quantity"] == 5


@pytest.mark.parametrize("answers, name, expected", [
    ([" МЫШЬ ", "0"], "мышь", {"quantity": 0, "price": 1200}),
    (["мышь", "8"], "мышь", {"quantity": 8, "price": 1200}),
    ([" Клавиатура ", "2", "2500.5"], "клавиатура", {"quantity": 2, "price": 2500.5}),
])
def test_console_updates_stock(app_env, interact, answers, name, expected):
    _, output = interact(app_env.app.add_storage_item, answers)
    assert "Ошибка" not in output
    assert app_env.storage.get_current_item(name) == expected


@pytest.mark.parametrize("answers", [
    [" "], ["мышь", "x"], ["мышь", "-1"],
    ["новый", "0", "10"], ["новый", "2", "-1"],
    ["новый", "2", "nan"], ["новый", "2", "inf"], ["новый", "2", "x"],
])
def test_console_stock_error_does_not_mutate_stock(app_env, interact, answers):
    before = app_env.storage.items
    _, output = interact(app_env.app.add_storage_item, answers)
    assert "Ошибка при изменении склада" in output
    assert app_env.storage.items == before


@pytest.mark.parametrize("assigned", [False, True])
def test_show_order_contains_details(app_env, order, capsys, assigned):
    if assigned:
        order.assign_courier(app_env.courier)
    app_env.app.show_order(order)
    output = capsys.readouterr().out
    for detail in ["ID: 1", "Статус: создан", "Клиент: Анна", "+79990000000",
                   "Невский, 1", "мышь (x2, 1200 руб.)", "Стандартная доставка",
                   "350.0 руб.", "3-5 дней", "Итого: 2750.0 руб.",
                   "Курьер: Иван" if assigned else "Курьер: Не назначен"]:
        assert detail in output


def test_show_orders_empty_and_multiple(app_env, make_order, capsys):
    app_env.app.show_orders()
    assert "Заказов нет" in capsys.readouterr().out
    app_env.orders.add_order(make_order(1))
    app_env.orders.add_order(make_order(2))
    app_env.app.show_orders()
    output = capsys.readouterr().out
    assert "ID: 1" in output and "ID: 2" in output


@pytest.mark.parametrize("choice, delivery, total", [
    ("1", StandardDelivery, 2750), ("2", ExpressDelivery, 2900), ("3", PickupDelivery, 2400),
])
def test_update_delivery(app_env, order, interact, choice, delivery, total):
    app_env.orders.add_order(order)
    _, output = interact(app_env.app.update_order_delivery, ["1", choice])
    assert isinstance(order.delivery_method, delivery)
    assert order.calculate_total_price() == total
    assert "Новая итоговая стоимость" in output


@pytest.mark.parametrize("action", ["update_order_delivery", "assign_courier", "change_order_status"])
@pytest.mark.parametrize("order_id", ["abc", "99"])
def test_order_commands_reject_invalid_id(app_env, order, interact, action, order_id):
    app_env.orders.add_order(order)
    _, output = interact(getattr(app_env.app, action), [order_id])
    assert "Ошибка" in output
    assert order.status == STATUS_CREATED
    assert order.courier is None
    assert app_env.courier.is_available


@pytest.mark.parametrize("choice", ["abc", "0", "4"])
def test_invalid_delivery_keeps_method(app_env, order, interact, choice):
    app_env.orders.add_order(order)
    method = order.delivery_method
    _, output = interact(app_env.app.update_order_delivery, ["1", choice])
    assert "Ошибка" in output
    assert order.delivery_method is method


def test_assignment_without_available_couriers(app_env, order, interact):
    app_env.orders.add_order(order)
    app_env.courier.mark_busy()
    _, output = interact(app_env.app.assign_courier, ["1"])
    assert "нет доступных курьеров" in output
    assert order.courier is None


@pytest.mark.parametrize("courier_id", ["abc", "99"])
def test_assignment_invalid_courier(app_env, order, interact, courier_id):
    app_env.orders.add_order(order)
    _, output = interact(app_env.app.assign_courier, ["1", courier_id])
    assert "Ошибка" in output
    assert order.courier is None
    assert app_env.courier.is_available


@pytest.mark.parametrize("command, method", [
    ("1", "create_order"), ("2", "show_orders"), ("3", "update_order_delivery"),
    ("4", "assign_courier"), ("5", "change_order_status"), ("6", "add_storage_item"),
    ("7", "show_items"),
])
def test_menu_dispatches_and_returns_to_menu(app_env, interact, monkeypatch, command, method):
    calls = []
    target = app_env.storage if command == "7" else app_env.app
    monkeypatch.setattr(target, method, lambda: calls.append(method))
    _, output = interact(app_env.app.run, [command, "0"])
    assert calls == [method]
    assert output.count("Выбрать доставку") == 2
    assert "Работа завершена" in output
