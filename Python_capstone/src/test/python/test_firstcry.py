import os
import time
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Shared state to continue browser session after login
is_logged_in = False

# ✅ Test Case 1: Login with Mobile Number and OTP
@allure.feature("Login")
def test_login_with_mobile_number_and_otp(driver):
    global is_logged_in
    wait = WebDriverWait(driver, 20)
    js = driver.execute_script

    allure.dynamic.title("TC_LOGIN_001 - Login with Mobile Number and OTP")
    driver.get("https://www.firstcry.com/")

    # Step 1: Click Login Button
    with allure.step("Clicking Login button"):
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Login')]")))
        js("arguments[0].scrollIntoView(true);", login_btn)
        login_btn.click()

    # Step 2: Enter Mobile Number
    with allure.step("Entering mobile number"):
        mobile_input = wait.until(EC.visibility_of_element_located((By.ID, "lemail")))
        mobile_input.clear()
        mobile_input.send_keys("9363025780")

    # Step 3: Click Continue
    with allure.step("Clicking Continue button"):
        continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='CONTINUE']")))
        continue_btn.click()

    # Step 4: Handle OTP
    if os.getenv("JENKINS_HOME"):
        otp = "123456"
        for i, ch in enumerate(otp):
            otp_field = wait.until(EC.visibility_of_element_located((By.ID, f"notp{i}")))
            otp_field.send_keys(ch)
        allure.attach("Auto-filled OTP (Jenkins environment)", "text/plain")
    else:
        with allure.step("Waiting for manual OTP entry (up to 60 seconds)"):
            otp_entered = wait_for_manual_otp_entry(driver, 60)
            assert otp_entered, "Manual OTP not entered in time"

    # Step 5: Click Submit
    with allure.step("Clicking Submit button"):
        submit_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class, 'loginSignup_submitOtpBtn_block')]/span[text()='SUBMIT']"
        )))
        submit_btn.click()

    # Step 6: Confirm login
    with allure.step("Verifying login success"):
        assert wait_for_login_success(driver), "Login failed after OTP"
        is_logged_in = True
        allure.attach("Login successful", "text/plain")


def wait_for_manual_otp_entry(driver, max_wait_seconds):
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        try:
            all_filled = all(driver.find_element(By.ID, f"notp{i}").get_attribute("value") for i in range(6))
            if all_filled:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def wait_for_login_success(driver):
    try:
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.visibility_of_element_located((
            By.XPATH, "//span[contains(text(),'My Account') or contains(text(),'Logout')]"
        )))
        return element.is_displayed()
    except Exception:
        url = driver.current_url.lower()
        return "firstcry.com" in url and "login" not in url


# ✅ Test Case 2: Search product and navigate to product page (Steps 1-4)
@allure.feature("Search")
@pytest.mark.dependency(depends=["test_login_with_mobile_number_and_otp"])
def test_search_and_open_product_page(driver):
    global is_logged_in
    if not is_logged_in:
        pytest.skip("Skipping search test because login was not successful")

    wait = WebDriverWait(driver, 30)
    js = driver.execute_script

    # Step 1: Search for a product
    with allure.step("Searching for product"):
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "search_box")))
        search_box.clear()
        search_box.send_keys("Babyhug Cosy Cosmo Stroller")
        search_btn = driver.find_element(By.CSS_SELECTOR, ".search-button")
        js("arguments[0].click();", search_btn)

    # Step 2: Click on the product
    with allure.step("Clicking product link"):
        product = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//a[contains(@title,'Babyhug Cosy Cosmo Stroller')]"
        )))
        js("arguments[0].scrollIntoView(true);", product)
        js("arguments[0].click();", product)

    # Step 3: Handle new tab
    original_tab = driver.current_window_handle
    for tab in driver.window_handles:
        if tab != original_tab:
            driver.switch_to.window(tab)
            allure.attach(f"Switched to new tab: {tab}", "text/plain")
            break

    # Step 4: Wait for product page to load
    with allure.step("Verifying product page load"):
        wait.until(EC.presence_of_element_located((By.ID, "prodImgInfo")))
        allure.attach(driver.current_url, "Product Page URL", allure.attachment_type.TEXT)


# ✅ Test Case 3: Add product to wishlist (Step 5)
@allure.feature("Wishlist")
@pytest.mark.dependency(depends=["test_search_and_open_product_page"])
def test_add_to_wishlist(driver):
    wait = WebDriverWait(driver, 20)
    js = driver.execute_script

    with allure.step("Adding product to wishlist"):
        wishlist = wait.until(EC.presence_of_element_located((By.XPATH, "//label[@data-fc-ricon='y']")))
        js("arguments[0].scrollIntoView(true);", wishlist)
        time.sleep(1)
        js("arguments[0].click();", wishlist)
        allure.attach("Added product to wishlist", "text/plain")


# ✅ Test Case 4: Add to cart and open wishlist (Steps 6-9)
@allure.feature("Cart & Wishlist")
@pytest.mark.dependency(depends=["test_add_to_wishlist"])
def test_add_to_cart_and_manage_wishlist(driver):
    wait = WebDriverWait(driver, 20)
    js = driver.execute_script

    # Step 6: Add to cart
    with allure.step("Adding product to cart"):
        js("window.scrollBy(0, 400);")
        add_to_cart_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'ADD TO CART')]")
        ))
        js("arguments[0].scrollIntoView(true);", add_to_cart_btn)
        time.sleep(1)
        js("arguments[0].click();", add_to_cart_btn)
        allure.attach("Added product to cart", "text/plain")

    # Step 7: Open cart
    with allure.step("Navigating to cart"):
        view_cart_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'cart-icon')]")))
        js("arguments[0].click();", view_cart_btn)
        allure.attach("Opened Cart page", "text/plain")
        time.sleep(2)

    # Step 8: Open wishlist from cart
    with allure.step("Opening wishlist"):
        heart_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ShortlistTab1']/a/span[1]")))
        js("arguments[0].scrollIntoView(true);", heart_icon)
        time.sleep(1)
        js("arguments[0].click();", heart_icon)
        allure.attach("Opened Wishlist page", "text/plain")

    # Step 9: Remove item from wishlist
    with allure.step("Removing item from wishlist"):
        remove_wishlist_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(@class,'delete_sec')]")))
        js("arguments[0].scrollIntoView(true);", remove_wishlist_item)
        time.sleep(1)
        js("arguments[0].click();", remove_wishlist_item)
        allure.attach("Removed item from Wishlist successfully", "text/plain")


# ✅ Test Case 5: Remove all items from cart (Step 10)
@allure.feature("Cart Cleanup")
@pytest.mark.dependency(depends=["test_add_to_cart_and_manage_wishlist"])
def test_remove_all_items_from_cart(driver):
    wait = WebDriverWait(driver, 20)
    js = driver.execute_script

    with allure.step("Navigating to cart and removing all items"):
        # Navigate to cart page
        cart_icon = wait.until(EC.element_to_be_clickable((By.ID, "cart_TotalCount")))
        js("arguments[0].scrollIntoView(true);", cart_icon)
        js("arguments[0].click();", cart_icon)
        allure.attach("Navigated to Cart page", "text/plain")
        time.sleep(3)

        # Remove all items
        while True:
            remove_buttons = driver.find_elements(
                By.XPATH,
                "//div[contains(@class,'shortcomm')]//span[contains(text(),'REMOVE') or contains(text(),'Remove')]"
            )
            allure.attach(f"Found {len(remove_buttons)} remove buttons", "text/plain")
            if not remove_buttons:
                allure.attach("Cart is empty now", "text/plain")
                break
            btn = remove_buttons[0]
            js("arguments[0].scrollIntoView(true);", btn)
            time.sleep(1)
            try:
                btn.click()
            except:
                js("arguments[0].click();", btn)
            time.sleep(2)
            allure.attach("Removed one item from cart", "text/plain")
