from appium.webdriver.common.touch_action import TouchAction

# Perform swipe down to refresh the accounts page
screen_size = driver.get_window_size()
start_x = screen_size['width'] * 0.5
start_y = screen_size['height'] * 0.2
end_y = screen_size['height'] * 0.8

action = TouchAction(driver)
action.press(x=start_x, y=start_y).wait(1000).move_to(x=start_x, y=end_y).release().perform()

time.sleep(5)  # Adjust the sleep time or replace with explicit wait
