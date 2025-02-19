import asyncio
from playwright.async_api import async_playwright

# Import semua file Playwright
import login_only_input_password
import login_only_input_phoneNumber

# Fungsi untuk menjalankan setiap file Playwright
async def run_all():
    async with async_playwright() as p:
        await login_only_input_password.open_bebeclub()
        await login_only_input_phoneNumber.open_bebeclub()

if __name__ == "__main__":
    asyncio.run(run_all())
