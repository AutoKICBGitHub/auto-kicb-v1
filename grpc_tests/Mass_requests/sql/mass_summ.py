# Импорт данных из файлов
from grpc_tests.Arrays.positive_customers_data import positive_customers
from grpc_tests.Mass_requests.sql.ind_list import ind_list

# Создаём пустой список для третьего массива
result = []

# Цикл по каждому элементу из operation_data
for operation in positive_customers:
    for ind in ind_list:
        # Создаем новый элемент, объединив данные из operation_data и ind_list
        combined_data = {
            "sessionkey": operation["sessionkey"],
            "accountIdDebit": operation["accountIdDebit"],
            "account_no": ind["account_no"],
            "full_name_lat": ind["full_name_lat"],
            "qrServiceId": ind["qrServiceId"]
        }
        result.append(combined_data)

# Сохранение в Python файл
with open("result.py", "w", encoding="utf-8") as f:
    f.write("result = [\n")
    for item in result:
        f.write(f"    {item},\n")
    f.write("]\n")

print("Массив успешно сохранён в result.py")
