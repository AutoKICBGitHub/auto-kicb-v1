import http.client
import json
from Grps_test_internet_equiring.new_data import data
from Grps_test_internet_equiring.tokens import tokens

def load_data_from_file(new_data):
    """Загружает данные из файла и возвращает их как словарь."""
    try:
        with open(new_data, "r", encoding='utf-8') as f:
            content = f.read()
            exec(content)  # Выполняем код, чтобы создать переменную data
        return data  # Возвращаем весь словарь data
    except Exception as e:
        print(f"Ошибка при загрузке данных из файла {new_data}: {e}")
        return {}

def load_tokens(tokens1):
    try:
        with open(tokens1, "r", encoding='utf-8') as f:
            content = f.read()
            exec(content)  # Выполняем код, чтобы создать переменную data
        return tokens  # Возвращаем весь словарь data
    except Exception as e:
        print(f"Ошибка при загрузке данных из файла {tokens1}: {e}")
        return {}

def make_request(transaction_id, otp):
    """Выполняет HTTP-запрос с заданными transactionId и otp."""
    conn = http.client.HTTPSConnection("127.0.0.1", 3036)
    payload = json.dumps({
        "transactionId": transaction_id,
        "otp": otp
    })
    headers = {
        'Authorization': tokens,
        'Content-Type': 'application/json'
    }

    conn.request("POST", "/internet-acquiring/create-transaction", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


# Загружаем данные из файла
data = load_data_from_file("new_data.py")

# Выполняем запрос для каждой записи
if data:
    for key, value in data.items():
        transaction_id = value['transactionId']
        otp = value['otp']
        make_request(transaction_id, otp)
else:
    print("Нет данных для обработки.")
