from pages.Internet_top_up_page import Intenet_and_tv_top_up_Page


def test_mobile_top_up(browser):
     page = browser
     top_up = Intenet_and_tv_top_up_Page(page)
     top_up.intenet_top_up_aknet()