import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import allure
import os
import time

# -----------------------------
# Browser fixture (session)
# -----------------------------
@pytest.fixture(scope="session")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


# -----------------------------
# Screenshot helper
# -----------------------------
def capture_screenshot(driver, test_name):
    screenshots_dir = os.path.join("src", "test", "resources", "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filepath = os.path.join(screenshots_dir, f"{test_name}_{timestamp}.png")
    driver.save_screenshot(filepath)
    return filepath


# -----------------------------
# Hook: Attach screenshot on failure
# -----------------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        if driver:
            test_name = item.name
            screenshot_path = capture_screenshot(driver, test_name)
            allure.attach.file(
                screenshot_path,
                name=f"{test_name}_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
