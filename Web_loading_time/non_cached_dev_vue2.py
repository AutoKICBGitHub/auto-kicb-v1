import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright
import os

def load_config():
    """Загрузка конфигурации из JSON файла."""
    try:
        with open('C:/project_kicb/Web_loading_time/config_dev/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Ошибка: файл config.json не найден")
        raise
    except json.JSONDecodeError:
        print("Ошибка: некорректный формат файла config.json")
        raise

def measure_loading_time():
    """Настройка браузера."""
    try:
        config = load_config()
        timings = {}  # Словарь для хранения замеров времени
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            
            # Создаем контекст с настройками записи видео
            context = browser.new_context(
                record_video_dir="./",  # Директория для сохранения видео
                record_video_size={"width": 1920, "height": 1080}  # Размер видео
            )
            
            # Получаем текущее время и номер теста для имени файла
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_number = len([f for f in os.listdir('./') if f.endswith('.webm')]) + 1
            
            # Устанавливаем имя файла для видео
            video_path = f"./test_recording_{current_time}_test{test_number}.webm"
            page = context.new_page()
            
            try:
                page.goto(config['url'])
                start_time1 = time.time()  # начало загрузки страницы логина
                page.wait_for_timeout(2000)
                
                # Проверяем, авторизован ли пользователь
                try:
                    page.locator("//div[contains(text(), 'Курсы валют')]").wait_for(
                        timeout=config['timeouts']['auth_timeout']
                    )
                    print("Пользователь уже авторизован, выполняем выход из системы")
                    # Выполняем выход из системы
                    page.locator("//img [@alt='log-out']").wait_for(timeout=config['timeouts']['default_timeout'])
                    page.locator("//img [@alt='log-out']").click()
                    time.sleep(2)  # Ждем завершения выхода
                    page.goto(config['url'])  # Возвращаемся на страницу логина
                
                except:
                    pass 
                print("Начинаем процесс авторизации")
                # Начинаем процесс логина
                start_time1 = time.time()  # начало загрузки страницы логина
                page.wait_for_timeout(2000)
                
                # Выполняем процесс логина
                page.wait_for_selector("input[type='text']")
                page.locator("input[type='text']").fill(config['credentials']['username'])
                page.locator("input[type='text']").press("Tab")
                page.wait_for_selector("input[type='password']")
                page.locator("input[type='password']").fill(config['credentials']['password'])
                page.locator("button:has-text('Войти')").click()
                end_time1 = time.time()  # конец авторизации
                timings['login_page_load_time'] = end_time1 - start_time1
                
                page.wait_for_selector(".confirm-otp__input")
                for index, digit in enumerate(config['credentials']['otp']):
                    page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)
                start_time2 = time.time()  # начало авторизации
                
                # Ждем появления конкретных элементов вместо networkidle
                page.wait_for_load_state('domcontentloaded')
                time.sleep(2)
                    

                # начало проверки загрузки главной страницы 
                page.locator("//span[contains(text(), '7 419.8 ₽')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//div [contains(text(), 'EUR')]").wait_for(timeout=config['timeouts']['default_timeout'])
                end_time2 = time.time()  # конец авторизации
                timings['auth_time'] = end_time2 - start_time2                    

                start_time3 = time.time()  # начало обмена валют
                # начало проверки загрузки страницы "Платежи"
                page.locator("//a[contains(text(),'Переводы')]").click()
                page.locator("//p[contains(text(), 'Между своими счетами')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//p[contains(text(),'Между своими счетами')]").click()
                page.locator("//h4 [contains(text(), 'Перевод между своими счетами')]").wait_for(timeout=config['timeouts']['default_timeout'])
                
                # Генерируем и сохраняем номер документа
                doc_number = str(random.randint(100000, 999999))
                page.locator("//p [contains(text(), 'Документа')] /..//input").fill(doc_number)
                page.locator("//p [contains(text(), 'Дата валютирования')] /..//input").clear()
                page.locator("//p [contains(text(), 'Дата валютирования')] /..//input").fill(datetime.now().strftime("%d.%m.%Y"))
                page.locator("//p [contains(text(), 'Выберите счет')]").nth(0).click()
                page.locator("//p [contains(text(), '1280010000885166')]").click()
                time.sleep(1)
                page.locator("//p [contains(text(), 'Выберите счет')]").click()
                page.locator("//p [contains(text(), '1285330001721111')]").click()
                page.locator("//p [contains(text(), 'Код платежа по классификатору')] /..//input").nth(0).fill("11111200")
                page.locator("//p [contains(text(), 'Сумма перевода')] /..//input").fill("10")
                page.locator("//button[contains(text(), 'Далее')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//button[contains(text(), 'Далее')]").click()
                page.locator("//button[contains(text(), 'Отправить на подтверждение')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//button[contains(text(), 'Отправить на подтверждение')]").click()
                page.locator("//a [contains(text(),'Транзакции на подтверждении')]").click()
                page.locator("//div [contains(text(),'Выбрать все')] ").click()  # Возвращаем выбор всех транзакций
                page.locator("//span[contains(text(), 'Подтвердить выбранные')]").click()
                page.locator("//p [contains(text(),'Вам выслан код на номер')]").wait_for(timeout=config['timeouts']['default_timeout'])
                for _ in range(6):
                    page.keyboard.press("1")
                page.locator("//span [contains(text(),'Транзакции успешно подтверждены')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//i [contains(text(), 'close')]").click()
                time.sleep(3)
                page.locator("//a [contains(text(),'История')]").click()
                page.locator(f"//div [contains(text(), '{doc_number}')]").wait_for(timeout=config['timeouts']['default_timeout'])
                # В истории ищем по номеру документа
                page.locator(f"//div [contains(text(), '{doc_number}')]").click()
                page.locator("//span[contains(text(), 'отправить транзакции в банк')]").click()
                page.locator("//span[contains(text(), 'Отправить в банк')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//span[contains(text(), 'Отправить в банк')]").click()
                page.locator("//span[contains(text(), 'OK')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//span[contains(text(), 'OK')]").click()
                # конец проверки перевод между своими счетами 
                end_time3 = time.time()  # конец обмена валют
                timings['currency_exchange_time'] = end_time3 - start_time3

                start_time4 = time.time()  # начало перевода между счетами
                # начало проверки перевод обмен валюты
                page.locator("//a [contains(text(),'Переводы')]").click()
                time.sleep(1)
                page.locator("//p [contains(text(),'Обмен валют')]").click()
                time.sleep(1)
                page.locator("//h4 [contains(text(), 'Обмен валют')]").wait_for(timeout=config['timeouts']['default_timeout'])
                time.sleep(1)
                
                # Генерируем и сохраняем номер документа для обмена валюты
                exchange_doc_number = str(random.randint(100000, 999999))
                page.locator("//p [contains(text(), 'Документа')] /..//input").fill(exchange_doc_number)
                page.locator("//p [contains(text(), 'Выберите счет')]").nth(0).click()
                page.locator("//p [contains(text(), '1280010000885166')]").click()
                time.sleep(1)
                page.locator("//p [contains(text(), 'Выберите счет')]").click()
                page.locator("//p [contains(text(), '1280010200885022')]").click()
                page.locator("//p [contains(text(), 'Сумма к списанию')] /..//input").fill("10")
                page.locator("//button[contains(text(), 'Далее')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//button[contains(text(), 'Далее')]").click()
                page.locator("//button[contains(text(), 'Отправить на подтверждение')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//button[contains(text(), 'Отправить на подтверждение')]").click()
                time.sleep(1)
                page.locator("//a [contains(text(),'Транзакции на подтверждении')]").click()
                page.locator("//div [contains(text(),'Выбрать все')] ").click()  # Возвращаем выбор всех транзакций
                page.locator("//span[contains(text(), 'Подтвердить выбранные')]").click()
                page.locator("//p [contains(text(),'Вам выслан код на номер')]").wait_for(timeout=config['timeouts']['default_timeout'])
                for _ in range(6):
                    page.keyboard.press("1")
                page.locator("//span [contains(text(),'Транзакции успешно подтверждены')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//i [contains(text(), 'close')]").click()
                
                
                time.sleep(1)
                page.locator("//a [contains(text(),'История')]").click()
                page.locator(f"//div [contains(text(), '{exchange_doc_number}')]").wait_for(timeout=config['timeouts']['default_timeout'])
                # В истории ищем по номеру документа
                page.locator(f"//div [contains(text(), '{exchange_doc_number}')]").click()
                page.locator("//span[contains(text(), 'отправить транзакции в банк')]").click()
                page.locator("//span[contains(text(), 'Отправить в банк')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//span[contains(text(), 'Отправить в банк')]").click()
                page.locator("//span[contains(text(), 'OK')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//span[contains(text(), 'OK')]").click()
                # конец проверки перевод обмен валюты
                end_time4 = time.time()  # конец перевода между счетами
                timings['internal_transfer_time'] = end_time4 - start_time4

                start_time5 = time.time()  # начало скачивания выписки
                page.locator("//a [contains(text(),'Счета')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//a [contains(text(),'Счета')]").click()
                page.locator("//span[contains(text(), '7 419.8 ₽')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//div[contains(text(), 'Курсы валют')]").wait_for(timeout=config['timeouts']['auth_timeout'])
                page.locator("//div [contains(text(), 'EUR')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//span [contains(text(), '1280010000885166')]").click()
                page.locator("//div [contains(text(), 'Выписка по счету')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//div [contains(text(), 'Выписка по счету')]").click()
                page.locator("//span[contains(text(), '2025')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//span[contains(text(), 'XLS')]").click()
                time.sleep(3)
                page.locator("//a [contains(text(),'Счета')]").wait_for(timeout=config['timeouts']['default_timeout'])
                page.locator("//a [contains(text(),'Счета')]").click()
                end_time5 = time.time()  
                timings['statement_download_time'] = end_time5 - start_time5

                # Сохраняем результаты замеров
                save_timing_results(timings)
                
                return timings
                
            finally:
                # Дожидаемся сохранения видео перед закрытием контекста
                logout_button = page.locator("//img [@alt='log-out']")
                logout_button.wait_for(state="visible", timeout=config['timeouts']['default_timeout'])
                time.sleep(2)
                logout_button.click()
                time.sleep(3)
                
                # Закрываем контекст и сохраняем видео
                context.close()
                
                # Переименовываем видео файл если он существует
                video_files = [f for f in os.listdir('./') if f.endswith('.webm')]
                if video_files:
                    latest_video = max(video_files, key=lambda x: os.path.getctime(os.path.join('./', x)))
                    os.rename(os.path.join('./', latest_video), video_path)
    except Exception as e:
        print(f"Ошибка при выполнении теста: {str(e)}")
        return None

def save_results(results, failed_tests):
    """Сохранение результатов в JSON файл."""
    successful_times = [t for t in results if t is not None]
    
    if not successful_times:
        print("Нет успешных тестов для анализа")
        return
        
    stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": len(results),
        "successful_tests": len(successful_times),
        "failed_tests": len(failed_tests),
        "average_time": sum(successful_times) / len(successful_times),
        "min_time": min(successful_times),
        "max_time": max(successful_times),
        "all_runs": [
            {"run": i+1, "time": t if t is not None else "failed"} 
            for i, t in enumerate(results)
        ],
        "failed_runs": failed_tests
    }
    
    filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\nРезультаты сохранены в файл: {filename}")

def save_timing_results(timings):
    """Сохранение результатов замеров времени в отдельный JSON файл."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result = {
        "timestamp": timestamp,
        "timings": {
            "login_page_loading": timings.get('login_page_load_time'),
            "authorization": timings.get('auth_time'),
            "currency_exchange": timings.get('currency_exchange_time'),
            "internal_transfer": timings.get('internal_transfer_time'),
            "statement_download": timings.get('statement_download_time'),
            "total_time": sum(timings.values())
        }
    }
    
    filename = f"timing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nРезультаты замеров времени сохранены в файл: {filename}")

def test_10_times():
    """Функция для выполнения теста 10 раз."""
    results = []
    failed_tests = []
    all_timings = []
    
    for i in range(10):
        print(f"\nЗапуск теста {i+1}/10")
        try:
            timings = measure_loading_time()
            if timings is not None:
                all_timings.append(timings)
                results.append(sum(timings.values()))  # Общее время выполнения
            else:
                results.append(None)
                failed_tests.append({"run": i+1, "error": "Test failed"})
        except Exception as e:
            print(f"Ошибка в тесте {i+1}: {str(e)}")
            results.append(None)
            failed_tests.append({"run": i+1, "error": str(e)})

    # Сохраняем общую статистику
    save_results(results, failed_tests)
    
    # Сохраняем детальную статистику по всем замерам
    save_detailed_statistics(all_timings)

def save_detailed_statistics(all_timings):
    """Сохранение детальной статистики по всем замерам."""
    if not all_timings:
        return
        
    def safe_average(key):
        """Безопасное вычисление среднего значения с проверкой наличия ключа"""
        values = [t[key] for t in all_timings if key in t]
        return sum(values) / len(values) if values else 0
        
    stats = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_runs": len(all_timings),
        "average_timings": {
            "login_page_loading": safe_average('login_page_load_time'),
            "authorization": safe_average('auth_time'),
            "currency_exchange": safe_average('currency_exchange_time'),
            "internal_transfer": safe_average('internal_transfer_time'),
            "statement_download": safe_average('statement_download_time')
        },
        "all_runs": all_timings
    }
    
    filename = f"detailed_timing_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\nДетальная статистика сохранена в файл: {filename}")

if __name__ == "__main__":
    test_10_times()
