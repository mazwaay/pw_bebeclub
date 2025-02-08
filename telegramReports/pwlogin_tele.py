import requests
import json
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv

# Ambil token dan chat ID dari GitHub Secrets

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Mengambil dari secret
CHAT_ID = os.getenv("CHAT_ID")  # Mengambil dari secret

def send_telegram_message(text, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, data=payload)
    return response

async def open_bebeclub():
    # Membuat folder reports jika belum ada
    report_folder = "reports"
    os.makedirs(report_folder, exist_ok=True)

    # Format timestamp untuk nama file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{report_folder}/test_report_{timestamp}.json"
    screenshot_filename = f"{report_folder}/screenshot_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "success"
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        try:
            await page.goto("https://bebeclub.co.id")
            report["steps"].append("Website bebeclub.co.id berhasil dibuka.")
            
            await page.locator("text=Aktifkan Semua Cookie").click()
            report["steps"].append("Button Cookies berhasil diklik.")

            await page.click("div[class='wrapper-not-logged-in'] a[class='btn-login']")
            report["steps"].append("Button Masuk header diklik.")

            await page.fill("input[name='username-login-password']", "081310096543")
            report["steps"].append("Nomor HP berhasil diinput.")

            await page.fill("input[id='password-login-password']", "Password1!")
            report["steps"].append("Password berhasil diinput.")

            await page.click("#loginPasswordAction")
            report["steps"].append("Button Login berhasil diklik.")

            await page.wait_for_selector("text=Login Berhasil")
            report["steps"].append("Berhasil login ke bebeclub.co.id.")
            
            # Simpan screenshot
            await page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename

        except Exception as e:
            report["status"] = "failed"
            report["error"] = str(e)
        
        finally:
            await browser.close()
            report["steps"].append("Browser ditutup.")

            # Simpan report ke file JSON
            with open(report_filename, "w") as f:
                json.dump(report, f, indent=4)

            print(f"Report tersimpan: {report_filename}")
            print(f"Screenshot tersimpan: {screenshot_filename}")
            
            # Kirim laporan ke Telegram
            message = f"**Tes Playwright: {report['status']}**\n"
            message += f"Timestamp: {report['timestamp']}\n"
            message += "\nLangkah-langkah:\n" + "\n".join(report["steps"])

            if report["status"] == "failed":
                message += f"\n\nError: {report.get('error', 'Tidak ada error')}"

            # Kirim pesan ke Telegram
            send_telegram_message(message)

if __name__ == "__main__":
    asyncio.run(open_bebeclub())
