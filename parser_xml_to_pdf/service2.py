from flask import Flask, request, jsonify
import requests
import xmltodict

app = Flask(__name__)


@app.route('/parse_xml', methods=['POST'])
def parse_xml():
    # Получаем XML-данные
    xml_data = request.data
    # Парсим XML в словарь
    data_dict = xmltodict.parse(xml_data)
    receipts = data_dict['receipts']['receipt']

    # Инициализируем массив товаров и бонусов
    items_array = []

    # Извлекаем товары из каждого receipt
    goods = receipts['goods']['good']
    # Проверяем, является ли goods списком или одним элементом
    if isinstance(goods, list):
        for good in goods:
            item = {
                "type": "good",
                "name": good["goodsName"],
                "quantity": int(good["baseCount"]),
                "price": float(good["price"]),
                "vatAmount": float(good["vatAmount"])
            }
            items_array.append(item)
    else:
        # Если goods - единственный элемент, добавляем его сразу
        item = {
            "type": "good",
            "name": goods["goodsName"],
            "quantity": int(goods["baseCount"]),
            "price": float(goods["price"]),
            "vatAmount": float(goods["vatAmount"])
        }
        items_array.append(item)

    # Извлекаем бонусы из каждого receipt, если они есть
    bonuses = receipts.get('bonuses', {}).get('bonus', [])
    # Проверяем, является ли bonuses списком или одним элементом
    if isinstance(bonuses, list):
        for bonus in bonuses:
            item = {
                "type": "bonus",
                "name": bonus["goodsName"],
                "quantity": int(bonus["baseCount"]),
                "price": float(bonus["price"]),
                "vatAmount": float(bonus["vatAmount"])
            }
            items_array.append(item)
    elif bonuses:
        # Если bonuses - единственный элемент, добавляем его сразу
        item = {
            "type": "bonus",
            "name": bonuses["goodsName"],
            "quantity": int(bonuses["baseCount"]),
            "price": float(bonuses["price"]),
            "vatAmount": float(bonuses["vatAmount"])
        }
        items_array.append(item)

    # Передаем массив в третий сервис
    response = requests.post('http://localhost:3002/create_pdf', json=items_array)

    return jsonify({"message": "Array sent to Service 3", "response": response.json()})


if __name__ == '__main__':
    app.run(port=3001)
