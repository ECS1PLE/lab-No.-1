import pytest

from storage import Storage


def test_add_normalizes_name_and_updates_price(storage):
    storage.add_items(" МЫШЬ ", 2, 1300)
    storage.add_items(" Клавиатура ", 1, 0)
    assert storage.items == {
        "мышь": {"quantity": 7, "price": 1300},
        "клавиатура": {"quantity": 1, "price": 0},
    }


@pytest.mark.parametrize("name, quantity, price", [
    ("", 1, 10), (" ", 1, 10), ("мышь", 0, 10), ("мышь", -1, 10),
    ("мышь", 1, -1), ("мышь", 1, float("nan")),
    ("мышь", 1, float("inf")), ("мышь", 1, float("-inf")),
])
def test_invalid_add_keeps_stock(storage, name, quantity, price):
    previous = storage.items
    with pytest.raises(ValueError):
        storage.add_items(name, quantity, price)
    assert storage.items == previous


def test_stock_views_are_independent_copies(storage):
    snapshot = storage.items
    snapshot["мышь"]["quantity"] = 999
    snapshot.clear()
    item = storage.get_current_item(" МЫШЬ ")
    item["price"] = 0
    assert storage.get_current_item("мышь") == {"quantity": 5, "price": 1200}


@pytest.mark.parametrize("quantity", [0, 2, 10])
def test_set_quantity_replaces_stock(storage, quantity):
    storage.set_quantity(" МЫШЬ ", quantity)
    assert storage.get_current_item("мышь") == {"quantity": quantity, "price": 1200}


@pytest.mark.parametrize("method, args", [
    ("set_quantity", ("нет", 1)), ("set_quantity", ("мышь", -1)),
    ("remove_items", ("нет",)), ("get_current_item", ("нет",)),
    ("take_items", ("нет", 1)), ("take_items", ("мышь", 0)),
    ("take_items", ("мышь", -1)), ("take_items", ("мышь", 6)),
    ("return_items", ("мышь", 0, 1200)), ("return_items", ("новый", 1, -1)),
])
def test_failed_operations_keep_stock(storage, method, args):
    previous = storage.items
    with pytest.raises(ValueError):
        getattr(storage, method)(*args)
    assert storage.items == previous


def test_take_and_remove(storage):
    storage.take_items(" МЫШЬ ", 2)
    assert storage.get_current_item("мышь")["quantity"] == 3
    storage.take_items("мышь", 3)
    assert storage.get_current_item("мышь")["quantity"] == 0
    storage.remove_items(" МЫШЬ ")
    assert storage.items == {}


def test_return_preserves_price_and_restores_missing_item(storage):
    storage.return_items(" МЫШЬ ", 2, 1000)
    assert storage.get_current_item("мышь") == {"quantity": 7, "price": 1200}
    storage.return_items(" Клавиатура ", 1, 2500)
    assert storage.get_current_item("клавиатура") == {"quantity": 1, "price": 2500}


def test_show_empty_and_populated_stock(storage, capsys):
    Storage().show_items()
    assert "Склад пуст" in capsys.readouterr().out
    storage.show_items()
    output = capsys.readouterr().out
    assert "мышь: 5 шт., 1200 руб." in output
