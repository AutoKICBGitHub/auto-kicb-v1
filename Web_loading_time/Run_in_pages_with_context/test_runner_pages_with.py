import json
import time
from playwright.sync_api import sync_playwright


def measure_loading_time():
    """Настройка браузера."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        user_data_dir = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default"
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False
        )
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

def test_50_times():
    """Функция для выполнения теста 50 раз."""
    total_time = 0
    results = []
    
    for i in range(50):
        print(f"\nЗапуск теста {i+1}/50")
        loading_time = measure_loading_time()
        total_time += loading_time
        results.append(loading_time)

    average_time = total_time / 50
    print(f"\nСреднее время загрузки за 50 тестов: {average_time:.2f} секунд")
    print(f"Минимальное время: {min(results):.2f} секунд")
    print(f"Максимальное время: {max(results):.2f} секунд")

if __name__ == "__main__":
    test_50_times()
