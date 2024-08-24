from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import csv

# Create a Chrome WebDriver instance with notifications disabled
def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--start-fullscreen")  # Start in full screen mode
    prefs = {"profile.default_content_setting_values.notifications": 2}  # Block notifications
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to read and print search terms from the file
def print_search_terms(filename):
    with open(filename, 'r') as file:
        search_terms = [line.strip() for line in file]
    print("Search terms from file:")
    for term in search_terms:
        print(term)
    return search_terms

# Function to perform search for a given term
def perform_search(driver, search_term):
    try:
        # Wait for the reveal button and click it
        reveal_button_xpath = '/html/body/div/div[1]/div[1]/nav/div/div/button[1]'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, reveal_button_xpath))
        ).click()

        # Find and interact with the search bar
        search_bar_xpath = '//input[@type="search"]'
        search_bar = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, search_bar_xpath))
        )

        print(f"Searching for term: {search_term}")
        search_bar.clear()
        search_bar.send_keys(search_term)
        search_bar.send_keys(Keys.ENTER)  # Press Enter to submit the search

        # Wait for the search results to be visible
        results_container_xpath = '//section[@id="search-results"]'
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, results_container_xpath))
        )

        # Wait for 5 seconds regardless of search results
        print("Waiting for 5 seconds...")
        time.sleep(5)
    
    except Exception as e:
        print(f"An error occurred during search: {e}")

# Function to add the first product from search results to the cart
def add_first_product_to_cart(driver):
    try:
        # Click on the first product in the search results
        first_product_xpath = '(//div[@class="w-full flex-none transform-gpu"]/img)[1]'
        first_product = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, first_product_xpath))
        )
        first_product.click()

        print("Product page loaded.")

        # Wait for the page to load completely
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//h1[@data-test-id="pdp-title"]'))
        )

        # Retrieve product details from the page
        product_name_xpath = '//h1[@data-test-id="pdp-title"]'
        product_price_xpath = '//*[@id="puma-skip-here"]/div/section/div[1]/section[2]/div/div[1]/div/div/span[1]'
        
        product_name = driver.find_element(By.XPATH, product_name_xpath).text
        product_price = driver.find_element(By.XPATH, product_price_xpath).text
        search_successful = "no"  # Initially assume failure
        print(f"Product Name: {product_name}")
        print(f"Product Price: {product_price}")

        # Define the CSV file path
        csv_file_path = 'product_details.csv'
        
        # Create CSV file if it does not exist
        if not os.path.exists(csv_file_path):
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Product Name", "Product Price", "Added to cart"])
        
        # Add to Cart button XPath
        add_to_cart_button_xpath = '//*[@id="puma-skip-here"]/div/section/div[1]/section[2]/div/div[7]/div[2]/button[1]'
        
        add_to_cart_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, add_to_cart_button_xpath))
        )
        print("Add to Cart button is clickable.")
        driver.execute_script("arguments[0].scrollIntoView();", add_to_cart_button)
        driver.execute_script("arguments[0].click();", add_to_cart_button)
        print("Add to Cart button clicked.")
        
        # Wait for the Add to Cart window to appear
        window_xpath = '//*[@data-test-id="minicart-added-to-content"]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, window_xpath))
        )
        print("Add to Cart window appeared.")
        
        # View Cart and Checkout button XPath
        view_and_checkout_button_xpath = '//*[@data-test-id="minicart-cart-link"]'
        view_and_checkout_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, view_and_checkout_button_xpath))
        )
        print("View and Checkout button is clickable.")
        driver.execute_script("arguments[0].scrollIntoView();", view_and_checkout_button)
        driver.execute_script("arguments[0].click();", view_and_checkout_button)
        print("View and Checkout button clicked.")
        
        # Wait for the page to redirect and verify the URL
        WebDriverWait(driver, 30).until(EC.url_contains("/cart"))
        current_url = driver.current_url
        
        # Check if redirected to the cart page
        if "/cart" in current_url:
            search_successful = "yes"
            print("Redirected to cart page:", current_url)
            print("Item successfully added to cart.")
        else:
            print("Not redirected to cart page.")
        
        # Print success message and wait for 3 seconds
        time.sleep(3)  # Stay on the cart page for 3 seconds

    except Exception as e:
        print(f"Error during add-to-cart operations: {e}")

    finally:
        # Append product details to the CSV file
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([product_name, product_price, search_successful])
        print("Product details added to CSV file.")

# Main execution function
def search_and_add_to_cart():
    driver = create_chrome_driver()
    driver.get('https://in.puma.com/in/en')

    try:
        # Read search terms from file
        search_terms_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'search_inputs.txt')
        search_terms = print_search_terms(search_terms_path)

        for term in search_terms:
            perform_search(driver, term)
            add_first_product_to_cart(driver)

    finally:
        print("Process completed successfully.")
        print("Closing browser.")
        driver.quit()

# Main execution
if __name__ == "__main__":
    search_and_add_to_cart()
