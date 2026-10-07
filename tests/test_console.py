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
    ("7", "show_items"), ("8", "add_courier"),
])
def test_menu_dispatches_and_returns_to_menu(app_env, interact, monkeypatch, command, method):
    calls = []
    target = app_env.storage if command == "7" else app_env.app
    monkeypatch.setattr(target, method, lambda: calls.append(method))
    _, output = interact(app_env.app.run, [command, "0"])
    assert calls == [method]
    assert output.count("Выбрать доставку") == 2
    assert "Работа завершена" in output


def test_menu_adds_courier_and_assigns_to_order(app_env, order, interact):
    app_env.orders.add_order(order)
    _, output = interact(app_env.app.run, [
        "8", " 2 ", " Петр ", " +79990000002 ", "4", "1", "2", "0",
    ])
    courier = app_env.couriers.get_courier_by_id(2)
    assert (courier.name, courier.phone) == ("Петр", "+79990000002")
    assert order.courier is courier
    assert not courier.is_available
    assert "8. Добавить курьера" in output
    assert "Курьер с ID 2 успешно добавлен" in output
    assert "Ошибка" not in output


@pytest.mark.parametrize("answers, message", [
    (["abc", "2", "Петр", "456"], "Ошибка:"),
    (["1.5", "2", "Петр", "456"], "Ошибка:"),
    (["0", "2", "Петр", "456"], "Введите положительное целое число"),
    (["-2", "2", "Петр", "456"], "Введите положительное целое число"),
    (["1", "2", "Петр", "456"], "Курьер с таким ID уже существует"),
    (["2", " \t", "Петр", "456"], "Поле не может быть пустым"),
    (["2", "Петр", " \t", "456"], "Поле не может быть пустым"),
])
def test_menu_retries_invalid_courier_field(app_env, interact, answers, message):
    _, output = interact(app_env.app.run, ["8", *answers, "0"])
    assert message in output
    assert "Работа завершена" in output
    courier = app_env.couriers.get_courier_by_id(2)
    assert (courier.name, courier.phone) == ("Петр", "456")
    assert courier.is_available
    assert app_env.couriers.get_all_couriers() == (app_env.courier, courier)


def test_duplicate_courier_id_reports_error_before_retry(app_env, monkeypatch, capsys):
    app_env.courier.mark_busy()
    prompts = []
    answers = iter(["1", "2", "Петр", "456"])

    def read(prompt):
        prompts.append(prompt)
        if len(prompts) == 2:
            assert prompt == "Введите ID нового курьера: "
            assert "Курьер с таким ID уже существует" in capsys.readouterr().out
            assert app_env.couriers.get_all_couriers() == (app_env.courier,)
        return next(answers)

    monkeypatch.setattr("builtins.input", read)
    app_env.app.add_courier()
    assert prompts == [
        "Введите ID нового курьера: ", "Введите ID нового курьера: ",
        "Введите имя курьера: ", "Введите телефон курьера: ",
    ]
    assert app_env.couriers.get_courier_by_id(2).name == "Петр"
    assert not app_env.courier.is_available


@pytest.mark.parametrize("name", ["Петр", "Анна-Мария", "Иван Петров", "O'Connor"])
def test_courier_name_accepts_letters_and_separators(app_env, interact, name):
    _, output = interact(app_env.app.add_courier, ["2", f" {name} ", "456"])
    assert app_env.couriers.get_courier_by_id(2).name == name
    assert "заново" not in output


@pytest.mark.parametrize("phone", ["456", "+79990000002"])
def test_courier_phone_accepts_digits_and_optional_plus(app_env, interact, phone):
    _, output = interact(app_env.app.add_courier, ["2", "Петр", f" {phone} "])
    assert app_env.couriers.get_courier_by_id(2).phone == phone
    assert "заново" not in output


def test_courier_fields_retry_immediately_and_preserve_previous_input(app_env, monkeypatch, capsys):
    steps = iter([
        ("ID нового курьера", "2", None),
        ("имя курьера", "Петр123", None),
        ("имя курьера", "123", "Введите имя заново"),
        ("имя курьера", "---", "Введите имя заново"),
        ("имя курьера", "Петр", "Введите имя заново"),
        ("телефон курьера", "abc", None),
        ("телефон курьера", "+", "Введите телефон заново"),
        ("телефон курьера", "++7999", "Введите телефон заново"),
        ("телефон курьера", "799+9", "Введите телефон заново"),
        ("телефон курьера", "799 9", "Введите телефон заново"),
        ("телефон курьера", "+79990000002", "Введите телефон заново"),
    ])

    def read(prompt):
        field, answer, error = next(steps)
        assert field in prompt
        if error:
            assert error in capsys.readouterr().out
            assert app_env.couriers.get_all_couriers() == (app_env.courier,)
        return answer

    monkeypatch.setattr("builtins.input", read)
    app_env.app.add_courier()
    assert list(steps) == []
    courier = app_env.couriers.get_courier_by_id(2)
    assert (courier.name, courier.phone) == ("Петр", "+79990000002")


@pytest.mark.parametrize("name, phone", [
    (" Анна-Мария ", " +79990000000 "),
    ("Иван Петров", "79990000000"),
    ("O'Connor", "123"),
])
def test_order_accepts_valid_client_name_and_phone(app_env, interact, name, phone):
    _, output = interact(app_env.app.create_order, [
        "1", "1", name, phone, "Адрес", "мышь", "1", "0", "1",
    ])
    client = app_env.orders.get_order_by_id(1).client
    assert (client.name, client.phone) == (name.strip(), phone.strip())
    assert "заново" not in output


def test_client_fields_retry_immediately_and_preserve_order_input(app_env, monkeypatch, capsys):
    steps = iter([
        ("ID заказа", "1", None),
        ("ID клиента", "2", None),
        ("имя клиента", "Анна123", None),
        ("имя клиента", "---", "Введите имя заново"),
        ("имя клиента", "Анна", "Введите имя заново"),
        ("телефон клиента", "abc", None),
        ("телефон клиента", "+", "Введите телефон заново"),
        ("телефон клиента", "++7999", "Введите телефон заново"),
        ("телефон клиента", "799 9", "Введите телефон заново"),
        ("телефон клиента", "+79990000000", "Введите телефон заново"),
        ("адрес клиента", "Адрес", None),
        ("название позиции", "мышь", None),
        ("количество позиции", "1", None),
        ("название позиции", "0", None),
        ("номер способа доставки", "1", None),
    ])

    def read(prompt):
        field, answer, error = next(steps)
        assert field in prompt
        if error:
            assert error in capsys.readouterr().out
            assert app_env.orders.get_all_orders() == ()
            assert app_env.storage.get_current_item("мышь")["quantity"] == 5
        return answer

    monkeypatch.setattr("builtins.input", read)
    app_env.app.create_order()
    assert list(steps) == []
    order = app_env.orders.get_order_by_id(1)
    assert (order.client.id, order.client.name, order.client.phone) == (
        2, "Анна", "+79990000000",
    )
