import json
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError

async def check_sticker_prices():
    # Создаем временную директорию для профиля
    with tempfile.TemporaryDirectory() as temp_dir:
        # Копируем данные профиля во временную директорию
        chrome_profile = Path(r"C:\Users\User\AppData\Local\Google\Chrome\User Data")
        temp_profile = Path(temp_dir) / "User Data"
        
        try:
            shutil.copytree(chrome_profile, temp_profile)
        except Exception as e:
            print(f"Ошибка копирования профиля: {e}")
            return

        async with async_playwright() as p:
            # Запускаем браузер с временным профилем
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=str(temp_profile),
                channel="chrome",
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-dev-shm-usage'
                ]
            )

            try:
                with open('stickers.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    stickers = data["stickers"]
            except FileNotFoundError:
                print("Файл stickers.json не найден")
                await browser_context.close()
                return
            except json.JSONDecodeError:
                print("Ошибка при чтении JSON файла")
                await browser_context.close()
                return

            base_url = "https://steamcommunity.com/market/search?q=\"{}\"&descriptions=1&category_730_ItemSet%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_Quality%5B%5D=#p1_price_asc"

            for sticker in stickers:
                try:
                    page = await browser_context.new_page()
                    url = base_url.format(sticker)
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    
                    try:
                        await page.wait_for_selector('.normal_price', state='visible', timeout=20000)
                        await asyncio.sleep(2)
                        
                        price_elements = await page.query_selector_all('.normal_price')
                        
                        if not price_elements:
                            print(f"Цены не найдены для {sticker}, ожидаем еще...")
                            await asyncio.sleep(3)
                            price_elements = await page.query_selector_all('.normal_price')
                        
                        found_good_price = False
                        
                        for price_element in price_elements:
                            price_text = await price_element.text_content()
                            try:
                                price_text = price_text.replace('$', '').replace('USD', '').strip()
                                price = float(price_text)
                                if 0 < price < 10:
                                    found_good_price = True
                                    print(f"Найдена подходящая цена для {sticker}: ${price} USD")
                                    break
                            except ValueError:
                                print(f"Не удалось преобразовать цену: {price_text}")
                                continue
                        
                        if not found_good_price:
                            print(f"Не найдено подходящих цен для {sticker}, закрываем страницу...")
                            await page.close()
                        else:
                            print(f"Оставляем открытой страницу для {sticker}")
                    
                    except TimeoutError:
                        print(f"Таймаут при ожидании цен для {sticker}")
                        await page.close()
                        
                except Exception as e:
                    print(f"Ошибка при обработке {sticker}: {str(e)}")
                    await page.close()
                    continue
                
                await asyncio.sleep(3)

            print("Поиск завершен!")
            await browser_context.close()

if __name__ == "__main__":
    asyncio.run(check_sticker_prices())
