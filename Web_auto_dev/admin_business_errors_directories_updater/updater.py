import time
from playwright.sync_api import sync_playwright
import random
import string
import os
import sys
import concurrent.futures


# Конфигурация
URL = "http://192.168.190.46:55556/admin-ui/"
LOGIN = "nurlanai"
PASSWORD = "Protokol1"
ITERATIONS = 100  # Количество обновлений для каждой вкладки
TABS_COUNT = 5    # Количество параллельных вкладок


def login(page):
    page.goto(URL)
    try:
        page.get_by_label("Login").click()
        page.get_by_label("Login").fill(LOGIN)
        page.get_by_label("Login").press("Tab")
        page.get_by_label("Password").fill(PASSWORD)
        page.get_by_label("Password").press("Enter")
        time.sleep(1.5)
        print("Вход в систему выполнен")
    except Exception as e:
        raise Exception(f"Ошибка входа в систему: {e}")


def update_directories(page):
    try:
        time.sleep(1.5)
        page.goto(URL + "business-error")
        time.sleep(1)
        # Ждем, пока страница загрузится
        print("Успешный переход на страницу директорий")
    except Exception as e:
        raise Exception(f"Ошибка при переходе на страницу директорий: {e}")


def search_directory(page):
    try:
        # Используем более надежный способ поиска поля ввода
        search_input = page.get_by_placeholder("Поиск")
        search_input.fill("INVALID_OTP")
        search_input.press("Enter")
        time.sleep(1.5)
        print("Успешный поиск директории")
    except Exception as e:
        raise Exception(f"Ошибка при поиске директории: {e}")


def generate_random_text(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def update_directory(page, tab_id):
    try:
        # Ждем, пока таблица загрузится
        page.wait_for_selector("table", timeout=5000)
        
        # Находим строку с INVALID_OTP
        row = page.locator("tr", has_text="INVALID_OTP").first
        
        # Нажимаем на кнопку редактирования в этой строке
        edit_button = row.locator("td.user-list__edit").first
        edit_button.click()
        time.sleep(1.5)
        
        # Генерируем случайный текст
        random_text = generate_random_text(15)
        
        # Находим поле ввода по классу
        input_field = page.locator("//input[@type='text']").nth(4)
        input_field.fill(random_text)
        
        edit_button = row.locator("td.user-list__edit").first
        edit_button.click()
        time.sleep(1.5)
        
        
        
        print(f"Вкладка {tab_id}: Текст ошибки успешно обновлен на: {random_text}")
        return True
    except Exception as e:
        print(f"Вкладка {tab_id}: Ошибка при обновлении директории: {e}")
        return False


def run_tab_updates(tab_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print(f"Вкладка {tab_id}: Запуск")
            login(page)
            update_directories(page)
            search_directory(page)
            
            success_count = 0
            for i in range(ITERATIONS):
                print(f"Вкладка {tab_id}: Итерация {i+1}/{ITERATIONS}")
                if update_directory(page, tab_id):
                    success_count += 1
                # Обновляем страницу для следующей итерации
                if i < ITERATIONS - 1:  # Не обновляем после последней итерации
                    update_directories(page)
                    search_directory(page)
            
            print(f"Вкладка {tab_id}: Завершено. Успешных обновлений: {success_count}/{ITERATIONS}")
        except Exception as e:
            print(f"Вкладка {tab_id}: Произошла ошибка: {e}")
        finally:
            time.sleep(1.5)
            browser.close()


def main():
    print(f"Запуск {TABS_COUNT} вкладок, каждая выполнит {ITERATIONS} обновлений")
    
    # Используем ThreadPoolExecutor для параллельного запуска вкладок
    with concurrent.futures.ThreadPoolExecutor(max_workers=TABS_COUNT) as executor:
        # Запускаем задачи для каждой вкладки
        futures = [executor.submit(run_tab_updates, i+1) for i in range(TABS_COUNT)]
        
        # Ждем завершения всех задач
        concurrent.futures.wait(futures)
    
    print("Все вкладки завершили работу")


if __name__ == "__main__":
    main()

