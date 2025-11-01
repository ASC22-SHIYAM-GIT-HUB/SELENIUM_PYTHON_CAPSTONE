import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import allure
import time
import os


@pytest.fixture(scope="session", autouse=True)
def setup_suite():
    """Setup once per test suite."""
    print("🚀 Browser launched once for the entire suite")

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    if driver:
        driver.quit()
        print("🧹 Browser closed after entire suite completed")


@pytest.fixture(autouse=True)
def setup_test(request, setup_suite):
    """Setup before each test and teardown after."""
    driver = setup_suite
    test_name = request.node.name
    print(f"🔹 Starting test: {test_name}")

    yield driver

    outcome = request.node.rep_call
    if outcome.failed:
        screenshot_path = capture_screenshot(driver, test_name)
        allure.attach.file(screenshot_path, name=test_name, attachment_type=allure.attachment_type.PNG)
        print(f"❌ Test Failed: {test_name}")
    elif outcome.passed:
        print(f"✅ Test Passed: {test_name}")
    else:
        print(f"⚠️ Test Skipped: {test_name}")


def capture_screenshot(driver, test_name):
    """Capture and save a screenshot inside src/test/resources/screenshots."""
    screenshots_dir = os.path.join("src", "test", "resources", "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filepath = os.path.join(screenshots_dir, f"{test_name}_{timestamp}.png")
    driver.save_screenshot(filepath)
    return filepath


def navigate_url(driver, url):
    """Utility method to navigate to a URL."""
    driver.get(url)
