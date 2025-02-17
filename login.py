from playwright.async_api import async_playwright

import asyncio

async def open_bebeclub():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page()

        try:
            await page.goto("https://generasimaju.co.id")
            print("Website bebeclub.co.id berhasil dibuka.")

            await page.locator("text=Aktifkan Semua Cookie").click()
            print("Button Cookies berhasil diklik.")

            await page.click("div[class='wrapper-not-logged-in'] a[class='btn-login']")
            print("Button Masuk header diklik.")

            await page.fill("input[name='username-login-password']", "081310096543")
            print("Nomor HP berhasil diinput.")

            await page.fill("input[id='password-login-password']", "Password1!")
            print("Password berhasil diinput.")

            await page.click("#loginPasswordAction")
            print("Button Login berhasil diklik.")

            await page.wait_for_selector("text=Login Berhasil")
            print("Berhasil login ke bebeclub.co.id.")

        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

        finally:
            await browser.close()
            print("Browser ditutup.")

if __name__ == "__main__":
    asyncio.run(open_bebeclub())
