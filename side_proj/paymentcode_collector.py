import asyncio
from playwright.async_api import async_playwright

async def get_payment_code(session_id):
    """Получает один код платежа"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print(f"Сессия {session_id}: Начинаю получение кода...")
            
            # Идём на главную страницу
            await page.goto("https://paytest.okmot.kg/")
            await asyncio.sleep(2)
            
            # Кликаем на кнопку "Пожертвовать"
            await page.locator("//input [@value='Пожертвовать']").click()
            await asyncio.sleep(2)

            # Выбираем банк
            await page.locator("//div [@class='bank-select']").nth(34).click()

            # Получаем код платежа
            payment_code = await page.locator("//p [@class='print-content code']  //label").text_content()
            print(f"Сессия {session_id}: Код платежа получен: {payment_code}")
            
            return payment_code
            
        except Exception as e:
            print(f"Сессия {session_id}: Ошибка - {e}")
            return None
        finally:
            await browser.close()

async def main():
    print("Запускаю параллельный сбор 15 кодов платежа...")
    
    # Создаём 15 задач для параллельного выполнения
    tasks = []
    for i in range(1, 16):
        task = get_payment_code(i)
        tasks.append(task)
    
    # Запускаем все задачи параллельно
    results = await asyncio.gather(*tasks)
    
    # Выводим результаты
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ СБОРА КОДОВ ПЛАТЕЖА:")
    print("="*50)
    
    valid_codes = []
    for i, code in enumerate(results, 1):
        if code:
            print(f"{i:2d}. {code}")
            valid_codes.append(code)
        else:
            print(f"{i:2d}. ОШИБКА - код не получен")
    
    print(f"\nУспешно получено кодов: {len(valid_codes)}/15")
    
    # Сохраняем в файл
    with open('payment_codes.txt', 'w', encoding='utf-8') as f:
        for i, code in enumerate(valid_codes, 1):
            f.write(f"{i}. {code}\n")
    
    print("Коды сохранены в файл payment_codes.txt")

if __name__ == "__main__":
    asyncio.run(main())
