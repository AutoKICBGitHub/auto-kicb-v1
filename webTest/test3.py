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

    page.fill('label:has-text("Категория DEFAULT")', "CategoryDef")
    page.fill('label:has-text("Категория RU")', "CategoryRu")
    page.fill('label:has-text("Категория KG")', "CategoryKg")
    page.fill('label:has-text("Категория ENG")', "CategoryEng")

    page.fill('label:has-text("Название DEFAULT")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("Название RU")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("Название KG")', generate_random_sentence('ky_KG'))
    page.fill('label:has-text("Название ENG")', generate_random_sentence('en_US'))

    page.click('label:nth-of-type(9) .q-field__native')
    page.click('xpath=/html/body/div[3]/div[2]/div[2]')

    page.fill('label:has-text("Tag")', "new")

    page.fill('label:has-text("orderValue")', str(random.randint(1, 10)))
    page.fill('label:has-text("serviceCode")', str(random.randint(1, 10000)))

    page.click('xpath=//*[@id="q-app"]/div/div[2]/div/form/div[1]/label[15]/div/div/div[1]/div[1]')
    time.sleep(0.5)
    page.click('xpath=/html/body/div[3]/div[2]/div[1]')

    page.click('xpath=/html/body/div[1]/div/div[2]/div/form/div[1]/label[16]/div/div/div[1]')
    time.sleep(0.5)
    page.click('xpath=/html/body/div[3]/div[2]/div[1]')


    page.fill('label:has-text("subTitle DEFAULT")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("subTitle ru")', generate_random_sentence('ru_RU'))
    page.fill('label:has-text("subTitle kg")', generate_random_sentence('ky_KG'))
    page.fill('label:has-text("subTitle eng")', generate_random_sentence('en_US'))

    page.click('xpath=/html/body/div[1]/div/div[2]/div/form/div[1]/div')
    page.click('xpath=/html/body/div[1]/div/div[2]/div/form/div[2]/button[2]/span[2]')

    context.close()
    browser.close()

with sync_playwright() as playwright:
    for i in range(5):
        print(f"Starting iteration {i+1}")
        run(playwright)
        print(f"Finished iteration {i+1}")
        time.sleep(1)


# with sync_playwright() as playwright:
#     run(playwright)
