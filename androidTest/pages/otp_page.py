from androidTest.utils.adb_utils import ADBUtils

class OTPPage:
    def __init__(self):
        self.adb = ADBUtils()

    def enter_otp(self, otp):
        self.adb.enter_text_via_adb(otp)
