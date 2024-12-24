from pages.phone_top_up_page import Top_up_Page


def test_mobile_top_up(browser):
     page = browser
     top_up = Top_up_Page(page)
     top_up.mobile_top_up()