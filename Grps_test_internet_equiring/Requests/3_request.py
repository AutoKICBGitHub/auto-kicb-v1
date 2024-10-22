import http.client
import json
from faker import Faker
from Grps_test_internet_equiring.tokens import tokens  # Импортируем массив токенов
from Grps_test_internet_equiring.phone_numbers import phone_numbers  # Импортируем массив номеров телефонов

# Создаем экземпляр Faker
fake = Faker()

# Словарь для хранения txnId
txn_ids = {}

# Цикл по каждому токену в массиве
for token in tokens:
    # Создаем HTTPS-соединение с сервером
    conn = http.client.HTTPSConnection("newibanktest.kicb.net")

    # Перебираем номера телефонов из phone_numbers
    for phone_number in phone_numbers:
        # Генерируем случайную сумму
        amount = round(fake.random_number(digits=5), 2)  # Генерируем случайную сумму (например, до 99999)

        # Создаем полезную нагрузку для запроса
        payload = json.dumps({
            "phoneNumber": phone_number,  # Используем номер телефона из массива
            "amount": amount  # Используем сгенерированную сумму
        })

        # Указываем заголовки
        headers = {
            'Authorization': f'Bearer {token}',  # Используем текущий токен
            'Content-Type': 'application/json'
        }

        # Делаем POST-запрос к серверу
        conn.request("POST", "/internet-acquiring/validate", payload, headers)

        # Получаем ответ от сервера
        res = conn.getresponse()
        data = res.read()
        response_json = json.loads(data.decode('utf-8'))  # Парсим ответ в JSON

        # Предположим, что txnId находится в response_json
        txn_id = response_json.get('txnId')  # Извлекаем txnId из ответа (проверьте правильный ключ в ответе)

        if txn_id:
            # Сохраняем txnId с наименованием txnId1, txnId2 и так далее
            txn_key = f'txnId{len(txn_ids) + 1}'  # Генерируем ключ с номером
            txn_ids[txn_key] = txn_id  # Сохраняем txnId в словарь

        # Печатаем ответ сервера
        print(f"Response for token {token} and phone number {phone_number}: {data.decode('utf-8')}")

    # Закрываем соединение после использования всех номеров для данного токена
    conn.close()

# Сохраняем txnIds в файл
with open("../txnIds.py", "w") as f:
    f.write("txnIds = {\n")  # Открывающая фигурная скобка
    for key, value in txn_ids.items():
        f.write(f'    "{key}": "{value}",\n')  # Форматируем каждую запись
    f.write("}\n")  # Закрывающая фигурная скобка
    print("Файл txnIds.py обновлен.")
