import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="ibank",
    user="postgres",
    password="postgres",
    port="5434"
)

# Создаем курсор
cursor = conn.cursor()

# Выполняем SQL-запрос
query = """
SELECT a.account_no, c.full_name_lat, a.account_class
FROM customers c
INNER JOIN accounts a ON a.customer_no = c.customer_no
WHERE a.acy_withdrawable_bal > 0
"""

cursor.execute(query)

# Получаем результаты
results = cursor.fetchall()

# Закрываем курсор и соединение
cursor.close()
conn.close()

# Преобразуем результаты в массив и применяем логику подстановки для qrServiceId
accounts_array = [{
    "account_no": row[0],
    "full_name_lat": row[1],
    "qrServiceId": "02" if row[2].startswith('3') else "01"
} for row in results]

# Сохраняем массив в Python-файл
with open('C:/project_kicb/grpc_tests/Mass_requests/sql/ind_list.py', 'w', encoding='utf-8') as f:
    f.write('ind_list = [\n')
    for item in accounts_array:
        f.write(f'    {item},\n')
    f.write(']\n')

print("Массив сохранен в файл ind_list.py")
