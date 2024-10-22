import psycopg2
import json

def get_phone_numbers_from_db():
    connection = None
    try:
        # Подключаемся к базе данных
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        # SQL-запрос для получения номеров телефонов пользователей
        query = "SELECT phone_number FROM users;"

        # Выполняем запрос
        cursor.execute(query)
        records = cursor.fetchall()

        # Вывод данных
        if records:
            print("Номера телефонов, возвращенные из базы данных:")
            for record in records:
                print(record[0])  # Печатаем только номер телефона
        else:
            print("Запрос не вернул данных.")

        return records

    except (Exception, psycopg2.Error) as error:
        print(f"Ошибка при работе с PostgreSQL:", error)
        return []

    finally:
        if connection:
            cursor.close()
            connection.close()

def update_phone_numbers(phone_numbers):
    """Очищает файл phone_numbers.py и записывает новые результаты"""
    with open("../phone_numbers.py", "w") as file:
        # Форматируем массив в JSON-совместимый формат с двойными кавычками
        json_data = json.dumps(phone_numbers, indent=4)
        # Записываем данные в файл
        file.write(f"phone_numbers = {json_data}\n")
        print("Файл phone_numbers.py обновлен.")

# Пример использования функции
phone_numbers_data = get_phone_numbers_from_db()

# Если запрос вернул данные, обновляем файл
if phone_numbers_data:
    # Создаем массив с номерами телефонов длиной 13 символов и без знака "+"
    phone_numbers = [
        record[0].replace("+", "") for record in phone_numbers_data if len(record[0]) == 13
    ]  # Извлекаем номера телефонов из записей, проверяя их длину и удаляя знак "+"

    # Обновляем файл phone_numbers.py только если есть подходящие номера
    if phone_numbers:
        update_phone_numbers(phone_numbers)
    else:
        print("Нет номеров телефонов длиной 13 символов для обновления phone_numbers.py.")
else:
    print("Нет данных для обновления phone_numbers.py.")
