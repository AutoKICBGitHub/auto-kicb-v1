import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

capabilities = {
    'platformName': 'Android',
    'automationName': 'uiautomator2',
    'deviceName': 'Android',
    'appPackage': 'net.kicb.ibankprod.dev',
    'appActivity': 'net.kicb.newibank.activity.MainActivity',
    'language': 'en',
    'locale': 'US',
    'platformVersion': '12'
}

capabilities_options = UiAutomator2Options().load_capabilities(capabilities)
appium_server_url = 'http://localhost:4723'

@pytest.fixture(scope="session")
def appium_driver():
    driver = webdriver.Remote(appium_server_url, options=capabilities_options)
    yield driver
    driver.quit()
