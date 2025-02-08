from playwright.async_api import async_playwright
import asyncio
import json
import datetime
import os

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
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
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

if __name__ == "__main__":
    asyncio.run(open_bebeclub())
