import sys
import os

# Добавляем родительскую директорию (корень проекта)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("Корень проекта:", parent_dir)
print("Python path:", sys.path[:3])

try:
    from src.external_api import convert_to_rub
    print("SUCCESS: Import works!")
    print("Функция:", convert_to_rub)
except ImportError as e:
    print(f"ERROR: {e}")
    print("Проверьте, есть ли папка src:", os.path.exists('src'))
    if os.path.exists('src'):
        print("Содержимое src:", os.listdir('src'))