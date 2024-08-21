# from appium.options.android import UiAutomator2Options
#
# from androidTest.useless_tests.test import login_in_sys
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
# adb_path = r'C:\platform-tools\adb.exe'
#
# def test(device):
#     login_in_sys()
