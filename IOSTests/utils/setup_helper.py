import subprocess
import os
from pathlib import Path


def print_device_info():
    """Вывод информации о доступных устройствах и симуляторах"""
    print("\n=== Доступные симуляторы ===")
    try:
        subprocess.run(["xcrun", "simctl", "list", "devices"])
    except Exception as e:
        print(f"❌ Ошибка при получении списка симуляторов: {e}")
    
    print("\n=== Проверка Xcode ===")
    try:
        subprocess.run(["xcode-select", "-p"])
    except Exception as e:
        print(f"❌ Ошибка при проверке Xcode: {e}")


def find_app_path():
    """Поиск .app файла в DerivedData"""
    derived_data = Path.home() / "Library/Developer/Xcode/DerivedData"
    print("\n=== Поиск .app файлов ===")
    
    if not derived_data.exists():
        print(f"❌ Папка {derived_data} не найдена")
        return
    
    found = False
    for path in derived_data.rglob("*.app"):
        found = True
        print(f"Найден .app файл: {path}")
    
    if not found:
        print("❌ .app файлы не найдены")
        print("Убедитесь, что проект собран в Xcode")


def check_appium():
    """Проверка установки и версии Appium"""
    try:
        result = subprocess.run(["appium", "-v"], 
                              capture_output=True, 
                              text=True)
        print(f"\n=== Версия Appium ===\n{result.stdout}")
        
        # Проверка драйвера XCUITest
        print("\n=== Проверка драйвера XCUITest ===")
        subprocess.run(["appium", "driver", "list"])
    except FileNotFoundError:
        print("\n❌ Appium не установлен. Выполните команды:")
        print("npm install -g appium")
        print("appium driver install xcuitest")


def check_simulator_status():
    """Проверка статуса симулятора"""
    print("\n=== Проверка симулятора ===")
    subprocess.run(["xcrun", "simctl", "list", "devices"])
    
    print("\n=== Проверка приложения ===")
    app_path = "/Users/test/Library/Developer/Xcode/DerivedData/ibank-anetmezjvzrbljdhlmcsbvolatty/Build/Products/Release-iphonesimulator/ibank.app"
    if os.path.exists(app_path):
        print(f"✅ Приложение найдено: {app_path}")
    else:
        print("❌ Приложение не найдено")


if __name__ == "__main__":
    print("=== Помощник настройки iOS тестов ===")
    print_device_info()
    find_app_path()
    check_appium() 