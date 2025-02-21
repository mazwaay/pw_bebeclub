import requests
import json
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv
import pytz  # Import pytz for timezone handling

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PASSWORD = os.getenv("PASSWORD")

# Telegram configuration
def send_telegram_message(text, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response

def send_telegram_photo(photo_path, chat_id=CHAT_ID, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        files = {"photo": photo}
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, files=files, data=payload)
    return response

# async configuration
async def open_bebeclub():
    report_folder = "reports.local"
    os.makedirs(report_folder, exist_ok=True)

    # Get the current time in Jakarta timezone (WIB)
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d%m%Y_%H%M%S")
    
    report_filename = f"{report_folder}/test_report_{timestamp}.json"
    screenshot_filename = f"{report_folder}/screenshot_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*"
    }
    
    # Start code here
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}) # view port size
        page = await context.new_page()

        try:
            await page.goto("https://bebeclub.co.id")
            report["steps"].append("Open the bebeclub website.")
            print("Open the bebeclub website.")
            
            await page.locator("text=Aktifkan Semua Cookie").click()
            report["steps"].append("Click the Aktifkan Semua Cookie button.")
            print("Click the Aktifkan Semua Cookie button.")

            await page.click("div[class='wrapper-not-logged-in'] a[class='btn-login']")
            report["steps"].append("Click the login button.")
            print("Click the login button.")

            await page.fill("input[name='password-login-password']", PASSWORD)
            report["steps"].append("Input the password.")
            print("Input the password.")

            button = await page.locator('//*[@id="loginPasswordAction"]').is_disabled()
            report["steps"].append(f"Verify the button login is disable? {button}")
            print(f"Verify the button login is disable? {button}")
            
            # Send report to telegram
            await page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename

        except Exception as e:
            report["status"] = "*failed*"
            report["error"] = str(e)
        
        finally:
            await browser.close()
            report["steps"].append("Close the browser.")

            # Save report to json file
            with open(report_filename, "w") as f:
                json.dump(report, f, indent=4)

            print(f"Report tersimpan: {report_filename}")
            print(f"Screenshot tersimpan: {screenshot_filename}")

            # Send report to telegram
            if os.path.exists(screenshot_filename):
                # Change the caption to use Jakarta time
                caption_time = datetime.datetime.now(jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")
                caption_steps = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(report["steps"])])
                caption = f"Update Time Zone Test: {report['status']}\n\nTest step:\n{caption_steps}\n\nCreate on:{caption_time}"
                
                # Send photo to telegram
                response = send_telegram_photo(screenshot_filename, caption=caption)
                print("Status kirim foto:", response.status_code)

if __name__ == "__main__":
    asyncio.run(open_bebeclub())
