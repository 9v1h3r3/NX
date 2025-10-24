import asyncio

import json

from playwright.async_api import async_playwright

# -------- CONFIG FILES --------

COOKIES_FILE = 'cookies.json'     # Your cookies/AppState

TID_FILE = 'tid.txt'              # Thread IDs (one per line)

TIME_FILE = 'time.txt'            # Interval per thread (seconds, one per line)

PREFIX_FILE = 'prefix.txt'        # Optional prefixes (one per line, empty line = no prefix)

MESSAGES_FILE = 'messages.txt'    # Messages to send

# -------- LOAD FILES --------

with open(COOKIES_FILE, 'r', encoding='utf-8') as f:

    cookies = json.load(f)

with open(TID_FILE, 'r', encoding='utf-8') as f:

    thread_ids = [line.strip() for line in f if line.strip()]

with open(TIME_FILE, 'r', encoding='utf-8') as f:

    intervals = [int(line.strip()) for line in f if line.strip()]

with open(PREFIX_FILE, 'r', encoding='utf-8') as f:

    prefixes = [line.strip() for line in f]

with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:

    messages = [line.strip() for line in f if line.strip()]

# -------- ASYNC FUNCTION TO SEND MESSAGES TO ONE THREAD --------

async def send_to_thread(thread_id, interval, prefix):

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)  # set True to run headless

        context = await browser.new_context()

        await context.add_cookies(cookies)

        page = await context.new_page()

        await page.goto(f'https://www.facebook.com/messages/e2ee/t/{thread_id}')

        await page.wait_for_selector('div[role="textbox"]')

        print(f'✅ Started sending messages to thread {thread_id}')

        while True:

            for message in messages:

                msg = f'{prefix} {message}'.strip()

                try:

                    await page.fill('div[role="textbox"]', msg)

                    await page.keyboard.press('Enter')

                    print(f'Sent to {thread_id}: {msg[:50]}')

                except Exception as e:

                    print(f'❌ Error sending to {thread_id}: {e}')

                await asyncio.sleep(interval)

# -------- MAIN FUNCTION TO START ALL THREADS --------

async def main():

    tasks = []

    for i, thread_id in enumerate(thread_ids):

        interval = intervals[i] if i < len(intervals) else 5

        prefix = prefixes[i] if i < len(prefixes) else ''

        tasks.append(asyncio.create_task(send_to_thread(thread_id, interval, prefix)))

    await asyncio.gather(*tasks)

# -------- RUN --------

asyncio.run(main())