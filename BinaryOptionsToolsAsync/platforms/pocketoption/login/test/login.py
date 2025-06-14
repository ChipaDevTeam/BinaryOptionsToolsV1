from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib.parse
from selenium_recaptcha_solver import RecaptchaSolver
from webdriver_manager.chrome import ChromeDriverManager
import time


def GetSSID(email, password):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    solver = RecaptchaSolver(driver=driver)
    driver.get("https://po.trade/login")  # https://po.trade/login
    driver.set_window_size(550, 691)
    driver.find_element(By.NAME, "email").click()
    driver.find_element(By.NAME, "email").send_keys(email)  # email@mail.com
    driver.find_element(By.NAME, "password").click()
    driver.find_element(By.NAME, "password").send_keys(password)  # password
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[2]/form/div[4]/button").click()
    recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
    try:
        solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[2]/form/div[4]/button").click()
    except:
        print("Cloud not solve captcha, please solve it and then press enter")
        input()
    WebDriverWait(driver, 30).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".layer"))
    )
    # For demo:
    driver.get(
        "https://po.trade/cabinet/demo-quick-high-low/"
    )  # https://po.trade/cabinet/demo-quick-high-low/
    WebDriverWait(driver, 30).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".layer"))
    )
    cookies = driver.get_cookies()
    session_token = [x["value"] for x in cookies if x["name"] == "ci_session"][0]
    decoded_string = urllib.parse.unquote(session_token)
    session = '42["auth", {"session": "' + decoded_string + '"}]'
    print(session)

    driver.quit()
    return session

