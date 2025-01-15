from typing import Dict
from pathlib import Path


class DeviceConfig:
    """Конфигурация устройств"""
    # Симулятор
    SIMULATOR_NAME = "iPhone 15 Pro"
    SIMULATOR_UDID = "A5220878-4496-471F-A7F8-A2295497EC35"
    SIMULATOR_VERSION = "17.5"
    BUNDLE_ID = "newibankprod.kicb.net"


def get_ios_simulator_capabilities() -> Dict:
    """
    Capabilities для iOS симулятора
    Документация: https://appium.io/docs/en/2.1/guides/caps/
    """
    return {
        # Основные настройки
        "platformName": "iOS",
        "appium:automationName": "XCUITest",
        "appium:deviceName": DeviceConfig.SIMULATOR_NAME,
        "appium:platformVersion": DeviceConfig.SIMULATOR_VERSION,
        "appium:bundleId": DeviceConfig.BUNDLE_ID,
        "appium:udid": DeviceConfig.SIMULATOR_UDID,
        
        # Дополнительные настройки
        "noReset": True,
        "fullReset": False,
        
        # Таймауты и логирование
        "newCommandTimeout": 3600,
        "wdaStartupRetries": 4,
        "wdaStartupRetryInterval": 20000,
        "printPageSourceOnFindFailure": True,
        "webDriverAgentLogging": True
    }


# Закомментировано до необходимости использования реального устройства
# def get_ios_real_device_capabilities() -> Dict:
#     """
#     Capabilities для реального iOS устройства
#     """
#     return {
#         # Основные настройки
#         "platformName": "iOS",
#         "platformVersion": DeviceConfig.DEVICE_VERSION,
#         "deviceName": DeviceConfig.DEVICE_NAME,
#         "udid": DeviceConfig.DEVICE_UDID,
#         "automationName": "XCUITest",
#         
#         # Путь к приложению
#         "app": AppPaths.REAL_DEVICE_APP,
#         
#         # Настройки для реального устройства
#         "xcodeOrgId": "",  # Team ID из Apple Developer аккаунта
#         "xcodeSigningId": "iPhone Developer",
#         "updatedWDABundleId": "com.facebook.WebDriverAgentRunner.custom",
#         
#         # Дополнительные настройки
#         "noReset": False,
#         "fullReset": False,
#         "wdaLocalPort": 8100,
#         
#         # Таймауты
#         "newCommandTimeout": 3600,
#         "wdaStartupRetries": 4,
#         "wdaStartupRetryInterval": 20000,
#         
#         # Логирование
#         "printPageSourceOnFindFailure": True,
#         "webDriverAgentLogging": True,
#     }
