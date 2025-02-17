import requests
import json
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
            "caption": caption
        }
        response = requests.post(url, files=files, data=payload)
    return response

def add_steps_to_image(screenshot_path, steps, output_path):
    # Buka gambar screenshot
    image = Image.open(screenshot_path)
    draw = ImageDraw.Draw(image)

    # Atur font dan warna
    font = ImageFont.load_default()
    text_color = (255, 0, 0)  # Warna merah untuk teks
    margin = 10
    line_height = 15

    # Tambahkan langkah-langkah di bagian bawah gambar
    y_text = image.height - (len(steps) * line_height) - margin
    for step in steps:
        draw.text((margin, y_text), step, font=font, fill=text_color)
        y_text += line_height

    # Simpan gambar baru
    image.save(output_path)

async def open_bebeclub():
    report_folder = "reports.local"
    os.makedirs(report_folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
    report_filename = f"{report_folder}/test_report_{timestamp}.json"
    screenshot_filename = f"{report_folder}/screenshot_{timestamp}.png"
    annotated_screenshot_filename = f"{report_folder}/screenshot_annotated_{timestamp}.png"

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
            print("Website bebeclub.co.id berhasil dibuka.")
            
            await page.locator("text=Aktifkan Semua Cookie").click()
            report["steps"].append("Button Cookies berhasil diklik.")
            print("Button Cookies berhasil diklik.")

            await page.click("div[class='wrapper-not-logged-in'] a[class='btn-login']")
            report["steps"].append("Button Masuk header diklik.")

            await page.fill("input[name='username-login-password']", "081310096543")
            report["steps"].append("Nomor HP berhasil diinput.")
            print("Nomor HP berhasil diinput.")

            await page.fill("input[id='password-login-password']", "Password1!")
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

            # Tambahkan langkah-langkah ke dalam screenshot
            steps_text = [f"{idx+1}. {step}" for idx, step in enumerate(report["steps"])]
            add_steps_to_image(screenshot_filename, steps_text, annotated_screenshot_filename)
            print(f"Screenshot dengan langkah-langkah: {annotated_screenshot_filename}")

            # Kirim laporan ke Telegram
            message = f"*Login dengan password: {report['status']}*\n"
            message += f"Timestamp: `{report['timestamp']}`\n"
            
            if report["status"] == "failed":
                message += f"\n\n*Error:* `{report.get('error', 'Tidak ada error')}`"

            # Kirim pesan teks ke Telegram
            send_telegram_message(message)
            
            # Kirim screenshot dengan langkah-langkah ke Telegram
            if os.path.exists(annotated_screenshot_filename):
                caption = f"Screenshot hasil tes: {report['status']}"
                response = send_telegram_photo(annotated_screenshot_filename, caption=caption)
                print("Status kirim foto:", response.status_code)

if __name__ == "__main__":
    asyncio.run(open_bebeclub())
