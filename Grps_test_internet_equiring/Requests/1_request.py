import http.client  # Импортируем модуль для работы с HTTP-запросами
import json  # Импортируем модуль для работы с JSON

# Массив с данными для логина (логин и пароль)
credentials = [
    {"login": "mashina.kg", "password": "password1"}  # Используем тот же логин повторно для примера
]

# Массив для хранения токенов
tokens = []


# Функция для получения токена
def get_token(login, password):
    # Создаем HTTPS-соединение с сервером
    conn = http.client.HTTPSConnection("newibanktest.kicb.net")

    # Создаем JSON-полезную нагрузку с логином и паролем
    payload = json.dumps({
        "login": login,
        "password": password
    })

    # Указываем заголовки
    headers = {
        'Content-Type': 'application/json'
    }

    # Делаем POST-запрос к серверу
    conn.request("POST", "/internet-acquiring/auth", payload, headers)

    # Получаем ответ от сервера
    res = conn.getresponse()

    # Читаем тело ответа
    data = res.read()

    # Преобразуем данные из JSON-строки в словарь
    response_json = json.loads(data.decode("utf-8"))

    # Извлекаем токен из 'accessToken', если он есть
    if 'accessToken' in response_json:
        return response_json['accessToken']
    else:
        print(f"Токен не найден для {login}: {response_json}")
        return None


# Цикл для перебора учетных данных
for cred in credentials:
    login = cred['login']
    password = cred['password']

    # Получаем токен для текущего логина и пароля
    token = get_token(login, password)

    # Если токен получен, добавляем его в массив токенов
    if token:
        tokens.append(token)

# Записываем токены в файл tokens.py

with open('../tokens.py', 'w') as f:
    f.write("tokens = [\n")  # Начинаем с объявления массива
    for token in tokens:
        f.write(f"    '{token}',\n")  # Записываем каждый токен с отступом
    f.write("]\n")  # Заканчиваем массив


# Выводим собранные токены
print("Собранные токены:", tokens)
