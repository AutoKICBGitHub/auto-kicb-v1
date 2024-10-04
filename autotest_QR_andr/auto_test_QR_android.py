import time
import subprocess
import pytest
import logging
from selenium.webdriver.common.by import By
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.options.android import UiAutomator2Options
from autotest_QR_andr.users import get_user

# Параметры для Appium
capabilities = {
    'platformName': 'Android',
    'automationName': 'uiautomator2',
    'deviceName': 'emulator-5554',
    'appPackage': 'net.kicb.ibankprod.dev',
    'appActivity': 'net.kicb.newibank.activity.MainActivity',
    'language': 'en',
    'locale': 'US',
    'platformVersion': '15'
}
adb_path = r'C:\\platform-tools\\adb.exe'
capabilities_options = UiAutomator2Options().load_capabilities(capabilities)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.parametrize("picture_number, user_id", [(i, str(j)) for j in range(1, 9) for i in range(12)])
def test_full_run(picture_number, user_id):
    # Запуск Appium-драйвера
    appium_server_url = 'http://localhost:4723'
    driver = webdriver.Remote(appium_server_url, options=capabilities_options)

    try:

        user = get_user(user_id)
        time.sleep(4)
        driver.find_element(AppiumBy.XPATH,
                                   '//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]').click()
        # Шаг 1: Ожидание загрузки полей логина
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((AppiumBy.ID, "net.kicb.ibankprod.dev:id/login_et"))
            )
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((AppiumBy.ID, "net.kicb.ibankprod.dev:id/password_et"))
            )
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((AppiumBy.ID, "net.kicb.ibankprod.dev:id/auth_progress_button"))
            )

            # Шаг 2: Ввод логина и пароля
            driver.find_element(AppiumBy.ID, "net.kicb.ibankprod.dev:id/login_et").send_keys(user['username'])
            driver.find_element(AppiumBy.ID, "net.kicb.ibankprod.dev:id/password_et").send_keys(user['password'])
            driver.find_element(AppiumBy.ID, "net.kicb.ibankprod.dev:id/auth_progress_button").click()
        except Exception as e:
            logger.error(f"Error waiting for elements: {e}")
            login_error_status = f"screenshot_login_failed_{user['account']}_{picture_number}.png"
            driver.get_screenshot_as_file(login_error_status)
            driver.quit()
        # Небольшая задержка для перехода на экран OTP
        time.sleep(4)

        # Шаг 3: Ввод OTP через ADB
        otp_command = f'{adb_path} shell input text {user["otp"]}'
        subprocess.run(otp_command, shell=True)
        time.sleep(5)

        otp_command = f'{adb_path} shell input text {user["otp"]}'
        subprocess.run(otp_command, shell=True)

        time.sleep(5)

        button_next = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((AppiumBy.XPATH,
                                              '//android.widget.FrameLayout[@resource-id="net.kicb.ibankprod.dev:id/button_frame_layout"]'))
        )
        button_next.click()

        time.sleep(5)

        otp_command = f'{adb_path} shell input text {user["otp"]}'
        subprocess.run(otp_command, shell=True)
        time.sleep(5)

        button_next = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((AppiumBy.XPATH,
                                              '//android.widget.FrameLayout[@resource-id="net.kicb.ibankprod.dev:id/button_frame_layout"]'))
        )
        button_next.click()

        time.sleep(5)

        button_ok = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((AppiumBy.ID, 'net.kicb.ibankprod.dev:id/positive_tv'))
        )
        button_ok.click()

        time.sleep(40)
        # WebDriverWait(driver, 60).until(
        #     EC.presence_of_element_located((AppiumBy.XPATH,
        #                                     '//android.widget.RelativeLayout[@resource-id="net.kicb.ibankprod.dev:id/bank_account_view"]'))
        # )
        time.sleep(5)
        # Клик на элемент "KICB QR"
        driver.find_element(AppiumBy.XPATH, '//android.widget.FrameLayout[@content-desc="KICB QR"]').click()
        time.sleep(4)
        # Вызов ADB команды для нажатия на разрешение (если нужно)
        allow_button = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (AppiumBy.ID, 'com.android.permissioncontroller:id/permission_allow_foreground_only_button'))
        )
        allow_button.click()
        time.sleep(5)
        # Клик на элемент QR-кода
        driver.find_element(AppiumBy.XPATH,
                            '//android.widget.Button[@resource-id="net.kicb.ibankprod.dev:id/qrCode"]').click()


        time.sleep(3)

        # Пример переключения на файловый менеджер
        # Ожидание загрузки изображений
        images = WebDriverWait(driver, 50).until(
            EC.visibility_of_all_elements_located((AppiumBy.ID, "com.google.android.documentsui:id/icon_thumb")))
        if not images:
            logger.warning("Элементы не найдены.")
        else:
            # Клик по изображению
            if picture_number < len(images):
                images[picture_number].click()
            else:
                logger.warning(f"Неверный номер изображения: {picture_number}.")

        time.sleep(20)

        change_account = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (AppiumBy.ID, 'net.kicb.ibankprod.dev:id/account_number'))
        )
        change_account.click()

        time.sleep(15)

        try:
            driver.find_element(
                By.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("{user["account"]}"))'
            )
            account_chooser = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH,
                                                  f'//android.widget.TextView[@resource-id="net.kicb.ibankprod.dev:id/account_number" and @text="{user["account"]}"]'))
            )

            # Клик по найденному элементу
            account_chooser.click()
        except Exception as e:
            logger.warning(f"Аккаунт {user['account']} не найден. Ошибка: {e}")
            # Нажимаем кнопку назад
            back_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((AppiumBy.ID, "net.kicb.ibankprod.dev:id/navigation_icon"))
                # Замените на правильный идентификатор кнопки «Назад»
            )
            back_button.click()

        # Ожидание видимости элемента после скролла

        time.sleep(3)
        input_field_value = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (AppiumBy.XPATH, '//android.widget.EditText[@resource-id="net.kicb.ibankprod.dev:id/amount_et"]'))
        )
        input_field_value.send_keys(
            "59.13")
        time.sleep(3)

        driver.find_element(AppiumBy.XPATH,
                            '//android.widget.FrameLayout[@resource-id="net.kicb.ibankprod.dev:id/button_frame_layout"]').click()

        time.sleep(5)
        transaction_status = f"screenshot_success_{user['account']}_{picture_number}.png"
        driver.get_screenshot_as_file(transaction_status)

        print(f"Скриншот сохранен по пути: {transaction_status}")

        approve_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((AppiumBy.XPATH,
                                        '//android.widget.FrameLayout[@resource-id="net.kicb.ibankprod.dev:id/button_frame_layout"]'))
        )
        approve_button.click()

        otp_command = f'{adb_path} shell input text {user["otp"]}'
        subprocess.run(otp_command, shell=True)
        time.sleep(3)
        driver.quit()
    except Exception as e:
        logger.error(f"Ошибка в тесте: {e}")
        error_status = f"screenshot_failed_{user['account']}_{picture_number}.png"
        driver.get_screenshot_as_file(error_status)

        print(f"Скриншот сохранен по пути: {error_status}")
        pytest.fail("Тест провален намеренно")
        driver.quit()



