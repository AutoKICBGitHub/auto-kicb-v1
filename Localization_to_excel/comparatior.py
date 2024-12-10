import pandas as pd
import re

def parse_js_to_keys(js_file_path):
    """Парсит ключи из JavaScript файла локализации."""
    keys = set()
    with open(js_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r'^\s*([\w_]+):', content, re.MULTILINE)  # Ищем ключи до двоеточия
        keys.update(matches)
    return keys


def find_missing_keys(excel_file, js_file):
    """Находит отсутствующие ключи из JS-файла, которые не попали в Excel."""
    # Считываем Excel-файл
    df = pd.read_excel(excel_file)

    # Проверка наличия столбца Key
    if 'Key' not in df.columns:
        raise ValueError("В Excel-файле отсутствует столбец 'Key'")

    # Извлекаем ключи из первого столбца Excel
    excel_keys = set(df['Key'])
    print(f"Ключи из Excel: {len(excel_keys)}")
    print(excel_keys)

    # Извлекаем ключи из JS-файла
    js_keys = parse_js_to_keys(js_file)
    print(f"Ключи из {js_file}: {len(js_keys)}")
    print(js_keys)

    # Находим отсутствующие ключи
    missing_keys = js_keys - excel_keys

    # Сохраняем отсутствующие ключи в файл
    with open("missing_keys.txt", "w", encoding="utf-8") as file:
        for key in sorted(missing_keys):
            file.write(f"{key}\n")

    print(f"Найдено отсутствующих ключей: {len(missing_keys)}")
    print("Отсутствующие ключи сохранены в 'missing_keys.txt'.")

# Укажите путь к Excel-файлу и JS-файлу
excel_file = "localization_multilingual.xlsx"
js_file = "en-us.js"

# Запуск поиска
find_missing_keys(excel_file, js_file)
