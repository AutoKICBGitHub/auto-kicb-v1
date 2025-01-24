import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright


def measure_loading_time():
    """Настройка браузера."""
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                page.goto("https://newibanktest.kicb.net/")
                page.wait_for_timeout(2000)

                # Проверяем, авторизован ли пользователь
                try:
                    # Ждем 5 секунд для появления элемента "Курсы валют"
                    page.locator("//div[contains(text(), 'Курсы валют')]").wait_for(timeout=5000)
                    print("Пользователь уже авторизован")
                except:
                    print("Требуется авторизация")
                    # Выполняем процесс логина
                    page.wait_for_selector("input[type='text']")
                    page.locator("input[type='text']").fill("aigerimk")
                    page.locator("input[type='text']").press("Tab")

                    page.wait_for_selector("input[type='password']")
                    page.locator("input[type='password']").fill("password1")
                    page.locator("button:has-text('Войти')").wait_for(timeout=300000)
                    time.sleep(3)
                    page.locator("button:has-text('Войти')").click()

                    page.wait_for_selector(".confirm-otp__input")
                    otp_code = "111111"
                    for index, digit in enumerate(otp_code):
                        page.locator(f"div:nth-child({index + 1}) > .confirm-otp__input").fill(digit)

                # Начинаем отсчет времени после авторизации
                start_time = time.time()
                
                # Тестирование навигации
                page.locator("//span[contains(text(), '29 522.16 ₸')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Платежи')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Платежи')]").click()
                page.locator("//p[contains(text(), 'ЭЛСОМ')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'История')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'История')]").click()
                page.locator("//span[@class='history-insert__main'][contains(text(), 'Сегодня')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Витрина')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Витрина')]").click()
                page.locator("//span[contains(text(), 'Получить справку по кредиту')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Сообщения')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Сообщения')]").click()
                page.locator("//div[contains(text(), 'Жалобы')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Профиль')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Профиль')]").click()
                page.locator("//div[contains(text(), 'Номер телефона')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Счета')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Счета')]").click()
                page.locator("//span[contains(text(), '29 522.16 ₸')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Платежи')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Платежи')]").click()
                page.locator("//p[contains(text(), 'ЭЛСОМ')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'История')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'История')]").click()
                page.locator("//span[@class='history-insert__main'][contains(text(), 'Сегодня')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Витрина')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Витрина')]").click()
                page.locator("//span[contains(text(), 'Получить справку по кредиту')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Сообщения')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Сообщения')]").click()
                page.locator("//div[contains(text(), 'Жалобы')]").wait_for(timeout=300000)

                page.locator("//a[contains(text(),'Профиль')]").wait_for(timeout=300000)
                page.locator("//a[contains(text(),'Профиль')]").click()
                page.locator("//div[contains(text(), 'Номер телефона')]").wait_for(timeout=300000)

                page.locator("//img [@alt='log-out']").wait_for(timeout=5000)
                page.locator("//img [@alt='log-out']").click()
                
                end_time = time.time()
                time.sleep(2)
                loading_time = end_time - start_time
                print(f"Время загрузки страницы: {loading_time:.2f} секунд")
                return loading_time
                
            finally:
                context.close()
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

def test_50_times():
    """Функция для выполнения теста 50 раз."""
    total_time = 0
    results = []
    failed_tests = []
    
    for i in range(50):
        print(f"\nЗапуск теста {i+1}/50")
        try:
            loading_time = measure_loading_time()
            if loading_time is not None:
                total_time += loading_time
                results.append(loading_time)
            else:
                results.append(None)
                failed_tests.append({"run": i+1, "error": "Test failed"})
        except Exception as e:
            print(f"Ошибка в тесте {i+1}: {str(e)}")
            results.append(None)
            failed_tests.append({"run": i+1, "error": str(e)})

    successful_times = [t for t in results if t is not None]
    if successful_times:
        average_time = sum(successful_times) / len(successful_times)
        print(f"\nСреднее время загрузки за успешные тесты: {average_time:.2f} секунд")
        print(f"Минимальное время: {min(successful_times):.2f} секунд")
        print(f"Максимальное время: {max(successful_times):.2f} секунд")
        print(f"Успешных тестов: {len(successful_times)} из {len(results)}")
    
    save_results(results, failed_tests)

if __name__ == "__main__":
    test_50_times()
