import sys
from pathlib import Path

# Добавляем корневую директорию в путь Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Проверка импорта (для отладки)
try:
    from src.external_api import convert_to_rub
    print(f"✓ Успешный импорт из src.external_api")
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")