from flask import Flask, request, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
import io

app = Flask(__name__)


@app.route('/create_pdf', methods=['POST'])
def create_pdf():
    # Получаем массив данных
    items = request.get_json()

    # Принудительно проверяем и декодируем текстовые данные
    for item in items:
        item["name"] = item["name"].encode('utf-8').decode('utf-8')
        item["type"] = "Товар" if item["type"] == "good" else "Бонус"

    # Определяем ширину страницы и максимальную ширину таблицы
    page_width = A4[0] - 2 * inch  # Оставляем поля по 1 дюйму с каждой стороны
    type_column_width = 0.9 * inch  # Устанавливаем фиксированную ширину для колонки "Тип"

    # Адаптивная ширина для колонки "Название"
    max_name_length = max(len(item["name"]) for item in items)
    name_column_width = min(4 * inch, max(2.5 * inch, max_name_length * 0.1 * inch))

    # Ширины для колонок с фиксированным количеством символов
    quantity_column_width = 0.6 * inch  # Для колонки "Кол-во", 4 символа
    vat_column_width = 0.5 * inch  # Для "НДС", также 4 символа
    price_column_width = 1 * inch  # Для "Цена", 10 символов
    total_column_width = 1 * inch  # Для "Сумма", 10 символов

    # Создаем буфер для PDF
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Регистрируем шрифт DejaVuSans для поддержки русского языка
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    # Стили для документа
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 18
    title_style.alignment = 1  # Центровка
    title_style.fontName = 'DejaVuSans'  # Используем зарегистрированный шрифт

    # Заголовок квитанции
    elements = []
    elements.append(Paragraph("Квитанция", title_style))
    elements.append(Spacer(1, 0.25 * inch))

    # Подзаголовок
    subheader_style = styles['Heading2']
    subheader_style.fontName = 'DejaVuSans'
    elements.append(Paragraph("Сводка товаров и бонусов", subheader_style))
    elements.append(Spacer(1, 0.15 * inch))

    # Обновлённые заголовки таблицы
    table_data = [["Тип", "Название", "Кол-во", "Цена", "НДС", "Сумма"]]
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),  # Установка шрифта для всей таблицы
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Добавляем строки товаров и бонусов
    for item in items:
        total_price = float(item["quantity"]) * float(item["price"])
        row = [
            item["type"],  # Принудительное декодирование в UTF-8
            item["name"],
            item["quantity"],
            f"{item['price']:.2f}",
            f"{item['vatAmount']:.2f}",
            f"{total_price:.2f}"
        ]
        table_data.append(row)

    # Создаем таблицу и добавляем стили, используя рассчитанную ширину для каждой колонки
    table = Table(table_data,
                  colWidths=[type_column_width, name_column_width, quantity_column_width, price_column_width,
                             vat_column_width, total_column_width])
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    # Итоги квитанции
    total_amount = sum(float(item["quantity"]) * float(item["price"]) for item in items)
    summary_style = styles['Heading3']
    summary_style.fontName = 'DejaVuSans'
    elements.append(Paragraph(f"Итоговая сумма: {total_amount:.2f} KGS", summary_style))

    # Генерация PDF
    pdf.build(elements)
    buffer.seek(0)

    # Сохраняем PDF-файл
    with open("receipt_output.pdf", "wb") as f:
        f.write(buffer.getbuffer())

    return jsonify({"message": "PDF создан успешно", "filename": "receipt_output.pdf"})


if __name__ == '__main__':
    app.run(port=3002)
