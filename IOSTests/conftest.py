import pytest
from appium import webdriver
from utils.capabilities import get_ios_simulator_capabilities, get_ios_real_device_capabilities


def pytest_addoption(parser):
    parser.addoption("--device", action="store", default="simulator",
                    help="Choose device: real or simulator")


@pytest.fixture(scope="session")
def driver(request):
    device = request.config.getoption("--device")
    
    if device == "real":
        capabilities = get_ios_real_device_capabilities()
    else:
        capabilities = get_ios_simulator_capabilities()
    
    driver = webdriver.Remote(
        command_executor='http://localhost:4723',
        desired_capabilities=capabilities
    )
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def setup():
    # Подготовка перед каждым тестом
    yield
    # Очистка после каждого теста
