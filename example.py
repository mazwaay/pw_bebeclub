from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com")
    page.locator("text=")

    # Membuat locator
    element = page.locator("text=More information")
    element.click()

    time.sleep(5000)
    # browser.close()