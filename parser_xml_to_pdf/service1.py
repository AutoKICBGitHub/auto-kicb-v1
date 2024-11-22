from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route('/upload_xml', methods=['POST'])
def upload_xml():
    try:
        # Получаем XML-файл от клиента

        xml_data = request.data

        # Отправляем XML второму сервису
        response = requests.post('http://localhost:3001/parse_xml', data=xml_data)

        # Проверка успешного ответа
        if response.status_code == 200:
            # Попытка обработать ответ как JSON
            try:
                response_json = response.json()
            except ValueError:
                response_json = {"message": "Received non-JSON response from Service 2", "content": response.text}
        else:
            response_json = {"error": f"Service 2 returned status code {response.status_code}"}

        return jsonify({"message": "XML sent to Service 2", "response": response_json})
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=3000)
