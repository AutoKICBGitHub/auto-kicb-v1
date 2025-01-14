from typing import Dict
from pathlib import Path


class AppPaths:
    """Пути к приложениям для разных окружений"""
    SIMULATOR_APP = "/Users/test/Library/Developer/Xcode/DerivedData/ibank-anetmezjvzrbljdhlmcsbvolatty/Build/Products/Release-iphonesimulator/ibank.app"
    # Закомментировано до необходимости использования реального устройства
    # REAL_DEVICE_APP = "/Users/test/Library/Developer/Xcode/DerivedData/ibank-anwwmamrkuoagnhbxdnjtklmduwj/Build/Products/Release-iphoneos/ibank.app"


class DeviceConfig:
    """Конфигурация устройств"""
    # Симулятор
    SIMULATOR_NAME = "iPhone 15 Pro"
    SIMULATOR_UDID = "A5220878-4496-471F-A7F8-A2295497EC35"
    SIMULATOR_VERSION = "17.5"
    
    # Закомментировано до необходимости использования реального устройства
    # # Реальное устройство
    # DEVICE_NAME = "iPhone"
    # DEVICE_UDID = ""
    # DEVICE_VERSION = "17.5"


def get_ios_simulator_capabilities() -> Dict:
    """
    Capabilities для iOS симулятора
    Документация: https://appium.io/docs/en/2.1/guides/caps/
    """
    return {
        # Основные настройки
        "platformName": "iOS",
        "platformVersion": DeviceConfig.SIMULATOR_VERSION,
        "deviceName": DeviceConfig.SIMULATOR_NAME,
        "udid": DeviceConfig.SIMULATOR_UDID,
        "automationName": "XCUITest",
        
        # Путь к приложению
        "app": AppPaths.SIMULATOR_APP,
        
        # Дополнительные настройки
        "noReset": False,  # Не сохранять состояние между запусками
        "fullReset": False,  # Не удалять приложение после теста
        "wdaLocalPort": 8100,  # Порт для WebDriverAgent
        
        # Таймауты
        "newCommandTimeout": 3600,  # Время ожидания новой команды (в секундах)
        "wdaStartupRetries": 4,  # Количество попыток запуска WDA
        "wdaStartupRetryInterval": 20000,  # Интервал между попытками (в мс)
        
        # Логирование
        "printPageSourceOnFindFailure": True,  # Выводить XML страницы при ошибках поиска
        "webDriverAgentLogging": True,  # Включить логи WDA
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
