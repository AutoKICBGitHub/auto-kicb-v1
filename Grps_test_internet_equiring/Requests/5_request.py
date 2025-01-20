import sys
import os
import json
import http.client

# Получаем абсолютный путь к файлу data.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
data_path = os.path.join(parent_dir, 'data.py')

# Загружаем данные из data.py
def load_data():
    try:
        with open(data_path, 'r') as f:
            content = f.read()
            local_dict = {}
            exec(content, {}, local_dict)
            return local_dict.get('data', {})
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return {}

data = load_data()

def save_new_data_to_file(data, filename):
    """Создает новый файл new_data.py и сохраняет в него данные с transactionId и otp."""
    try:
        with open(filename, "w", encoding='utf-8') as f:
            f.write("data = {\n")
            for txn_id, otp in data.items():
                f.write(f"    '{txn_id}': {{'transactionId': '{txn_id}', 'otp': '{otp}'}},\n")
            f.write("}\n")
        print(f"Файл {filename} успешно создан и обновлён с добавлением данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в файл {filename}: {e}")

# Указываем имя файла
filename = "C:/project_kicb/Grps_test_internet_equiring/new_data.py"

# Сохраняем данные в новый файл
save_new_data_to_file(data, filename)