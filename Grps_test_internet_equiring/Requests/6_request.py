import sys
import os
import json
import http.client
from Grps_test_internet_equiring.tokens import tokens  # импортируем массив токенов
from Grps_test_internet_equiring.new_data import data  # импортируем словарь с данными

# Получаем абсолютный путь к файлам
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Загружаем токен из JSON файла
with open(os.path.join(parent_dir, 'tokens.json'), 'r') as f:
    token_data = json.load(f)
    access_token = token_data['access_token']

# Проверяем наличие токена
if not access_token:
    print("Нет доступного токена")
    exit(1)

# Загружаем данные из new_data.py
def load_data():
    try:
        with open(os.path.join(parent_dir, 'new_data.py'), 'r') as f:
            content = f.read()
            local_dict = {}
            exec(content, {}, local_dict)
            return local_dict.get('data', {})
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return {}

data = load_data()

# Убедитесь, что у вас есть хотя бы один токен
if not tokens:
    print("Нет доступных токенов")
    exit(1)

# Создаем соединение с HTTPS
conn = http.client.HTTPSConnection("newibanktest.kicb.net")

# Словарь для хранения ответов
responses = {}

# Итерируемся по всем элементам data
for transaction_id, transaction_data in data.items():
    payload = json.dumps({
        "transactionId": transaction_data['transactionId'],
        "otp": transaction_data['otp']
    })

    # Используем первый токен из массива (можно адаптировать, если нужно использовать несколько токенов)
    headers = {
        'Authorization': f'Bearer {tokens[0]}',  # подставляем токен
        'Content-Type': 'application/json'
    }

    # Выполняем POST-запрос
    try:
        conn.request("POST", "/internet-acquiring/create-transaction", payload, headers)
        # Получаем ответ
        res = conn.getresponse()
        response_data = res.read()

        # Сохраняем ответ в словарь
        responses[transaction_id] = response_data.decode('utf-8')
        print(f"Response for transactionId {transaction_id}: {responses[transaction_id]}")

    except Exception as e:
        print(f"Error occurred for transactionId {transaction_id}: {str(e)}")
        responses[transaction_id] = f"Error: {str(e)}"

# Закрываем соединение
conn.close()

# Сохраняем все данные в файл otp_input_status.py
with open('C:/project_kicb/Grps_test_internet_equiring/otp_input_status.py', 'w', encoding='utf-8') as f:
    f.write('# Сохраненные ответы\n')
    f.write('responses = ')
    f.write(json.dumps(responses, ensure_ascii=False, indent=4))

print("Ответы сохранены в файл otp_input_status.py")
