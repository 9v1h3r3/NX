import asyncio
import json
import os
import time
from playwright.async_api import async_playwright

# ========== SAFE FILE READERS ==========
def safe_read(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return default

def safe_read_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception:
        return []

# ========== CONFIG FILES ==========
THREAD_ID = safe_read("tid.txt")
INTERVAL = float(safe_read("time.txt", "5"))
PREFIX = safe_read("prefix.txt")
MESSAGES = safe_read_lines("messages.txt")

# ========== COOKIE HANDLING ==========
if not os.path.exists("cookies.json") or os.stat("cookies.json").st_size == 0:
    print("⚠️ cookies.json missing or empty! Please upload valid cookies.")
    COOKIES = []
else:
    try:
        with open("cookies.json", "r", encoding="utf-8") as f:
            COOKIES = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON in cookies.json! Using empty cookie list.")
        COOKIES = []

# ========== MAIN BOT ==========
async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        if COOKIES:
            await context.add_cookies(COOKIES)
        page = await context.new_page()

        print("🌐 Logging in to Messenger...")
        await page.goto("https://www.facebook.com/messages")
        await page.wait_for_timeout(5000)

        if "login" in page.url.lower():
            print("❌ Login failed — invalid cookies.")
            await browser.close()
            return

        print("✅ Logged in successfully!")

        if not THREAD_ID:
            print("❌ tid.txt is empty! Add your E2EE thread ID (e.g. 1234567890).")
            await browser.close()
            return

        url = f"https://www.facebook.com/messages/e2ee/t/{THREAD_ID}"
        await page.goto(url)
        print(f"📨 Chat opened: {THREAD_ID}")

        while True:
            for msg in MESSAGES:
                full_msg = f"{PREFIX} {msg}".strip()
                try:
                    await page.fill('div[role="textbox"]', full_msg)
                    await page.keyboard.press("Enter")
                    print(f"✅ Sent: {full_msg[:40]}")
                except Exception as e:
                    print(f"⚠️ Send error: {e}")
                await asyncio.sleep(INTERVAL)

# ========== EXECUTION ==========
if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")
    except Exception as e:
        print(f"🔥 Fatal error: {e}")
