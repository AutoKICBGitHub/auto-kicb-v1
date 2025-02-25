import os
from PIL import Image

def resize_icon(image_path, output_path, size=(32, 32)):
    # Открываем изображение
    with Image.open(image_path) as img:
        # Изменяем размер с использованием оптимального алгоритма ресэмплинга
        img = img.resize(size, Image.LANCZOS)
        # Сохраняем изменённое изображение
        img.save(output_path)

def compress_icon(input_path, output_path, max_size_kb=10):
    """
    Сжимает иконку до указанного размера файла с максимальным сохранением качества
    """
    img = Image.open(input_path)
    original_mode = img.mode
    
    # Начинаем с большего размера
    max_dimension = 256  # Увеличиваем начальный размер
    ratio = max_dimension / max(img.size)
    if ratio < 1:  # Уменьшаем только если картинка больше max_dimension
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.LANCZOS)

    # Сначала пробуем сохранить как PNG с оптимизацией
    try:
        img.save(output_path, 'PNG', optimize=True)
        file_size = os.path.getsize(output_path) / 1024

        if file_size <= max_size_kb:
            return
    except:
        pass

    # Если PNG слишком большой, пробуем уменьшать размер, сохраняя формат
    current_size = img.size
    while max(current_size) > 96:  # Не уменьшаем меньше 96 пикселей
        new_size = tuple(int(dim * 0.9) for dim in current_size)  # Более плавное уменьшение
        img = img.resize(new_size, Image.LANCZOS)
        current_size = new_size
        
        try:
            img.save(output_path, 'PNG', optimize=True)
            file_size = os.path.getsize(output_path) / 1024
            
            if file_size <= max_size_kb:
                return
        except:
            pass

    # Только если PNG всё ещё слишком большой, переходим на JPEG
    if original_mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background

    # Начинаем с высокого качества JPEG
    quality = 95
    while quality > 60:  # Не опускаем качество ниже 60
        try:
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            file_size = os.path.getsize(output_path) / 1024
            
            if file_size <= max_size_kb:
                return
        except:
            pass
        
        quality -= 5

    # В крайнем случае, немного уменьшаем размер, сохраняя высокое качество JPEG
    while max(img.size) > 96:
        new_size = tuple(int(dim * 0.9) for dim in img.size)
        img = img.resize(new_size, Image.LANCZOS)
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        
        file_size = os.path.getsize(output_path) / 1024
        if file_size <= max_size_kb:
            return

def process_icons_folder():
    """
    Обрабатывает все иконки из папки 'иконки' и сохраняет в 'пережатые иконки'
    """
    input_folder = "иконки"
    output_folder = "пережатые иконки"
    
    # Создаем папки, если они не существуют
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Обрабатываем все файлы в папке
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            
            try:
                compress_icon(input_path, output_path)
                print(f"Обработан файл: {filename}")
            except Exception as e:
                print(f"Ошибка при обработке {filename}: {str(e)}")

if __name__ == "__main__":
    process_icons_folder()