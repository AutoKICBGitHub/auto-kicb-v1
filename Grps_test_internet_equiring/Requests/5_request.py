from Grps_test_internet_equiring.data import data

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