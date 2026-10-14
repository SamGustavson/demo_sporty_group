from __future__ import annotations
from selenium.common import TimeoutException
from selenium.webdriver.common.by import ByType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)


    def find(self, by: ByType, value: str) -> WebElement:
        return self.wait.until(EC.presence_of_element_located((by, value)))


    def find_clickable(self, by: ByType, value: str) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable((by, value)))


    def find_all(self, by: ByType, value: str) -> list[WebElement]:
        return self.wait.until(EC.presence_of_all_elements_located((by, value)))


    def is_present(self, by: ByType, value: str, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return True
        except TimeoutException:
            print('WebDriverWait failed')
            return False

    def _text(self, locator: tuple[str, str]) -> str:
        return self.wait.until(EC.visibility_of_element_located(locator)).text.strip()
