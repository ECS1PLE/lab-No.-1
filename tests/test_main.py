from pathlib import Path
import runpy
import subprocess
import sys

from main import main


def test_main_full_delivery_scenario(interact):
    _, output = interact(main, [
        "7", "1", "1", "1", "Анна", "123", "Невский, 1", "мышь", "2", "0", "1",
        "4", "1", "1", "5", "1", "подтвержден", "5", "1", "в пути",
        "5", "1", "доставлен", "2", "7", "0",
    ])
    assert "клавиатура: 10 шт., 2500 руб." in output
    assert "роблокс: 5 шт., 15000 руб." in output
    assert "мышь: 13 шт., 1200 руб." in output
    assert "ID: 2, Имя: Алексей" in output
    assert "Статус: доставлен" in output
    assert "Итого: 2750.0 руб." in output
    assert "Ошибка" not in output


def test_main_script_entrypoint(interact):
    script = Path(__file__).resolve().parents[1] / "main.py"
    _, output = interact(lambda: runpy.run_path(str(script), run_name="__main__"), ["0"])
    assert "Работа завершена" in output


def test_launch_in_fresh_python_process():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "main.py")], input="7\n0\n", text=True,
        capture_output=True, cwd=root, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "мышь: 15 шт., 1200 руб." in result.stdout
    assert "Работа завершена" in result.stdout
