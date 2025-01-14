from typing import Dict


def get_ios_simulator_capabilities() -> Dict:
    return {
        "platformName": "iOS",
        "platformVersion": "17.2",  # Версия iOS в симуляторе
        "deviceName": "iPhone 15",  # Название устройства в симуляторе
        "automationName": "XCUITest",
        "app": "/path/to/your/app.app",  # Путь к вашему .app файлу
        "noReset": False
    }


def get_ios_real_device_capabilities() -> Dict:
    return {
        "platformName": "iOS",
        "platformVersion": "17.2",  # Версия iOS на реальном устройстве
        "deviceName": "iPhone",  # Название вашего устройства
        "udid": "your-device-udid",  # UDID вашего устройства
        "automationName": "XCUITest",
        "app": "/path/to/your/app.ipa",  # Путь к вашему .ipa файлу
        "noReset": False,
        "xcodeOrgId": "your-team-id",  # ID вашей команды разработчиков
        "xcodeSigningId": "iPhone Developer"
    }
