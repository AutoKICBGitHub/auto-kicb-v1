from AndroidTests.utils.adb_utils import ADBUtils_otp

class OTPPage:
    def __init__(self):
        self.adb = ADBUtils_otp()

    def enter_otp(self, otp):
        self.adb.enter_text_via_adb(otp)

