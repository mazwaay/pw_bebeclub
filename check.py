import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")
print(f"CHAT_ID: {CHAT_ID}")