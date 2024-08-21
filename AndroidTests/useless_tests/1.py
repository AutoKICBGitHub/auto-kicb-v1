# import subprocess
# import time
#
# import pytest
# from appium import webdriver
# from appium.webdriver.common.appiumby import AppiumBy
# from appium.options.android import UiAutomator2Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
#
#
#
# capabilities = {
#     'platformName': 'Android',
#     'automationName': 'uiautomator2',
#     'deviceName': 'Android',
#     'appPackage': 'net.kicb.ibankprod.dev',
#     'appActivity': 'net.kicb.newibank.activity.MainActivity',
#     'language': 'en',
#     'locale': 'US',
#     'platformVersion': '12'
# }
# capabilities_options = UiAutomator2Options().load_capabilities(capabilities)
# appium_server_url = 'http://localhost:4723'
#
#
# adb_path = r'C:\platform-tools\adb.exe'
#
#
# @pytest.fixture()
# def driver():
#     app_driver = webdriver.Remote(appium_server_url, options=capabilities_options)
#     yield app_driver
#     app_driver.quit()
#
#
# def login_in_sys(driver):
#     try:
#         username_field = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((AppiumBy.ID, "net.kicb.ibankprod.dev:id/login_et")))
#         username_field.click()
#         username_field.send_keys("00727272")
#
#         password_field = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((AppiumBy.ID, "net.kicb.ibankprod.dev:id/password_et")))
#         password_field.click()
#         password_field.send_keys("password1")
#
#         login_submit_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((AppiumBy.ID, "net.kicb.ibankprod.dev:id/button_frame_layout")))
#         login_submit_button.click()
#
#     except TimeoutException as e:
#         print(f"TimeoutException: {e}")
#     except Exception as e:
#         print(f"Exception: {e}")
#
# def enter_otp_via_keyboard(otp):
#     time.sleep(2)
#     command = f'{adb_path} shell input text {otp}'
#     subprocess.run(command, shell=True)
#
#
# def click_by_coordinates(x, y):
#     command = f'{adb_path} shell input tap {x} {y}'
#     subprocess.run(command, shell=True)
#
#
# def enter_pin_code_via_adb(pin_code):
#     time.sleep(2)
#     command = f'{adb_path} shell input text {pin_code}'
#     subprocess.run(command, shell=True)
#
# def phone_password():
#     x = 106
#     y = 2240
#     z = 750
#     c = 1100
#     time.sleep(1)
#     click_by_coordinates(x, y)
#     enter_pin_code_via_adb("3385")
#     click_by_coordinates(z, c)
#
# def test_login(driver):
#     login_in_sys(driver)
#     otp = "111111"
#     enter_otp_via_keyboard(otp)
#     phone_password()