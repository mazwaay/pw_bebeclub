import requests
import json
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PASSWORD = os.getenv("PASSWORD")

def send_telegram_message(text, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"  # Menambahkan parse_mode untuk menggunakan Markdown
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
            "parse_mode": "Markdown"  # Menambahkan parse_mode untuk menggunakan Markdown
        }
        response = requests.post(url, files=files, data=payload)
    return response

async def open_bebeclub():
    report_folder = "reports.local"
    os.makedirs(report_folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
    report_filename = f"{report_folder}/test_report_{timestamp}.json"
    screenshot_filename = f"{report_folder}/screenshot_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*"  # Menambahkan * untuk teks tebal
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # context = await browser.new_context(no_viewport=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}) # Mengubah ukuran viewport
        page = await context.new_page()

        try:
            await page.goto("https://bebeclub.co.id")
            report["steps"].append("Website bebeclub.co.id berhasil dibuka.")
            print("Website bebeclub.co.id berhasil dibuka.")
            
            await page.locator("text=Aktifkan Semua Cookie").click()
            report["steps"].append("Button Cookies berhasil diklik.")
            print("Button Cookies berhasil diklik.")

            await page.click("div[class='wrapper-not-logged-in'] a[class='btn-login']")
            report["steps"].append("Button Masuk header diklik.")
            print("Button Masuk header diklik.")

            await page.fill("input[name='username-login-password']", PHONE_NUMBER)
            report["steps"].append("Nomor HP berhasil diinput.")
            print("Nomor HP berhasil diinput.")

            await page.fill("input[id='password-login-password']", PASSWORD)
            report["steps"].append("Password berhasil diinput.")
            print("Password berhasil diinput.")

            await page.click("#loginPasswordAction")
            report["steps"].append("Button Login berhasil diklik.")
            print("Button Login berhasil diklik.")

            await page.wait_for_selector("text=Login Berhasil")
            report["steps"].append("Berhasil login ke bebeclub.co.id.")
            print("Berhasil login ke bebeclub.co.id.")
            
            # Simpan screenshot
            await page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename

        except Exception as e:
            report["status"] = "*failed*"  # Mengubah status menjadi tebal jika gagal
            report["error"] = str(e)
        
        finally:
            await browser.close()
            report["steps"].append("Browser ditutup.")

            # Simpan report ke file JSON
            with open(report_filename, "w") as f:
                json.dump(report, f, indent=4)

            print(f"Report tersimpan: {report_filename}")
            print(f"Screenshot tersimpan: {screenshot_filename}")
            
            # Kirim laporan ke Telegram dengan status tebal
            message = f"*Login dengan password: {report['status']}*\n\n"  # Menambahkan enter setelah status
            message += f"Timestamp: {report['timestamp']}\n"  # Menambahkan baris baru setelah timestamp
            message += "\nLangkah-langkah:\n" + "\n".join(report["steps"])

            if report["status"] == "*failed*":
                message += f"\n\nError: {report.get('error', 'Tidak ada error')}"

            # Kirim pesan ke Telegram
            send_telegram_message(message)

            # Kirim screenshot dengan langkah-langkah ke Telegram
            if os.path.exists(screenshot_filename):
                # Ubah langkah-langkah jadi caption
                caption_steps = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(report["steps"])])
                caption = f"Login with password: {report['status']}\nLangkah-langkah:\n{caption_steps}"
                
                # Kirim gambar dengan caption yang sudah diubah
                response = send_telegram_photo(screenshot_filename, caption=caption)
                print("Status kirim foto:", response.status_code)

if __name__ == "__main__":
    asyncio.run(open_bebeclub())
