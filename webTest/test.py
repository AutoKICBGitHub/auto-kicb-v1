import time
from faker import Faker
from playwright.sync_api import sync_playwright
import random

def generate_random_word(language):
    if language == 'ru_RU':
        return Faker('ru_RU').word()
    elif language == 'en_US':
        return Faker('en_US').word()
    elif language == 'ky_KG':
        kyrgyz_words = ['китеп', 'чөй', 'орук', 'жашыл', 'майрам', 'акыл']
        return random.choice(kyrgyz_words)
    else:
        return ''

def generate_random_sentence(language):
    if language == 'ru_RU':
        return Faker('ru_RU').sentence()
    elif language == 'en_US':
        return Faker('en_US').sentence()
    elif language == 'ky_KG':
        return " ".join([generate_random_word('ky_KG') for _ in range(5)])
    else:
        return ''

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("http://192.168.190.46:55556/admin-ui/auth")

    page.fill('label:has-text("Login")', "admin")
    page.keyboard.press("Tab")
    page.fill('label:has-text("Password")', "Protokol1")
    page.keyboard.press("Enter")

    time.sleep(2)  # Wait for the page to load after login

    page.click('a:has-text("Сервисы")')
    page.click('button:has-text("создать новый")')

    page.fill('label:has-text("Название DEFAULT")', generate_random_word('ru_RU'))
    page.fill('label:has-text("Название RU")', generate_random_word('ru_RU'))
    page.fill('label:has-text("Название KG")', generate_random_word('ky_KG'))
    page.fill('label:has-text("Название ENG")', generate_random_word('en_US'))

    page.fill('label:has-text("Категория DEFAULT")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("Категория RU")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("Категория KG")', generate_random_sentence('ky_KG'))
    page.fill('label:has-text("Категория ENG")', generate_random_sentence('en_US'))

    page.click('label:nth-of-type(9) .q-field__native')
    page.wait_for_selector('div:has-text("gov"):nth-of-type(2)')
    page.click('div:has-text("gov"):nth-of-type(2)')

    page.fill('label:has-text("Tag")', generate_random_word('ru_RU'))

    page.fill('label:has-text("orderValue")', str(random.randint(1, 10)))
    page.fill('label:has-text("serviceCode")', str(random.randint(1, 10000)))

    page.click('label:nth-of-type(14) .q-field__native')
    page.wait_for_selector('div:has-text("SALYK")')
    options = page.locator('div:has-text("SALYK")')
    if options.count() > 0:
        random_option = random.randint(0, options.count() - 1)
        options.nth(random_option).click()
    else:
        print("No options found for 'SALYK'")

    page.click('label:nth-of-type(15) .q-field__native')
    page.wait_for_selector('div:has-text("да"):nth-of-type(2)')
    page.click('div:has-text("да"):nth-of-type(2)')
    page.click('label:nth-of-type(16) .q-field__native')
    page.wait_for_selector('div:has-text("да"):nth-of-type(2)')
    page.click('div:has-text("да"):nth-of-type(2)')

    page.fill('label:has-text("subTitle DEFAULT")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("subTitle ru")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("subTitle kg")', generate_random_sentence('ky_KG'))
    page.fill('label:has-text("subTitle eng")', generate_random_sentence('en_US'))

    page.click('label:has-text("Активировать")')
    page.click('button:has-text("Сохранить")')

    time.sleep(5)  # Wait for the save operation to complete

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)