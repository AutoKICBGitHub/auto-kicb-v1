import http.client  # Импортируем модуль для работы с HTTP-запросами
import json  # Импортируем модуль для работы с JSON

# Массив с данными для логина (логин и пароль)
credentials = [
    {"login": "amazon12", "password": "12345678"}  # Используем тот же логин повторно для примера
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
    
    # Проверяем наличие access и refresh токенов
    if 'access' in response_json and 'refresh' in response_json:
        return response_json  # Возвращаем весь ответ
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

# Изменим путь к файлу на абсолютный и используем .json вместо .py
token_file_path = 'C:\\project_kicb\\Grps_test_internet_equiring\\tokens.json'

# Сохраняем токен
try:
    with open(token_file_path, 'w') as f:
        json.dump({
            'access_token': token['access']['token'],
            'refresh_token': token['refresh']['token']
        }, f, indent=4)
    print(f"Токен успешно сохранен в {token_file_path}")
except Exception as e:
    print(f"Ошибка при сохранении токена: {e}")


# Выводим собранные токены
print("Собранные токены:", tokens)
