import pandas as pd
import os
from pathlib import Path

def replace_chars(text):
    replacements = {
        "»": "\"",
        "«": "\"",
        """: "\"",
        """: "\"",
        "'": "\"",
        "'": "\"",
        "′": "\"",
        "″": "\"",
        "‟": "\"",
        "„": "\"",
        "〝": "\"",
        "〞": "\"",
        "＂": "\"",
        "\u201c": "\"",  # Другой способ записи типографской открывающей кавычки
        "\u201d": "\"",  # Другой способ записи типографской закрывающей кавычки
        # Здесь можно добавить другие замены при необходимости
    }
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    return text

def parse_localization_excel(excel_path=None):
    if excel_path is None:
        # Ищем Excel файл в текущей директории
        current_dir = Path.cwd()
        excel_files = list(current_dir.glob('**/Перевод localization_multilingual (CN).xlsx'))
        if not excel_files:
            raise FileNotFoundError("Excel файл не найден. Пожалуйста, укажите правильный путь к файлу.")
        
        excel_path = excel_files[0]
    
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Файл не найден по пути: {excel_path}")
    
    try:
        # Читаем Excel файл
        print(f"Читаем файл: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Создаем список валидных строк
        valid_rows = []
        for index, row in df.iterrows():
            key = str(row.iloc[0])  # Первый столбец
            value = str(row.iloc[4])  # Четвертый столбец
            
            # Пропускаем строки, где ключ или значение пустые
            if pd.isna(key) or pd.isna(value) or key.strip() == '' or value.strip() == '':
                continue
            
            # Заменяем символы в значениях
            key = replace_chars(key)
            value = replace_chars(value)
            valid_rows.append(f"{key}:{value}")
        
        output_path = Path(excel_path).parent / 'localization_merged.txt'
        # Сохраняем результат в текстовый файл
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, row in enumerate(valid_rows):
                if i < len(valid_rows) - 1:
                    f.write(f"{row},\n")  # Добавляем запятую для всех строк кроме последней
                else:
                    f.write(row)  # Последняя строка без запятой
        
        print(f"Результат сохранен в: {output_path}")
        
    except Exception as e:
        print(f"Произошла ошибка при обработке файла: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        parse_localization_excel()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
