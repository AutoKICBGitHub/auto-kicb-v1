import http.client
import json
from Grps_test_internet_equiring.tokens import tokens  # импортируем массив токенов
from Grps_test_internet_equiring.new_data import data  # импортируем словарь с данными

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
