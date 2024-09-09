import subprocess
import time
from AndroidTests.conftest import adb_path

class ADBUtils:
    @staticmethod
    def enter_otp_via_adb(otp):
        command = f'{adb_path} shell input text {otp}'
        subprocess.run(command, shell=True)

    @staticmethod
    def click_by_coordinates(x, y):
        command = f'{adb_path} shell input tap {x} {y}'
        subprocess.run(command, shell=True)

    @staticmethod
    def enter_pin_code_via_adb(pin_code):
        time.sleep(2)
        command = f'{adb_path} shell input text {pin_code}'
        subprocess.run(command, shell=True)



