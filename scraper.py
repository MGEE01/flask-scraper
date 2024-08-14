import json
from datetime import datetime
from playwright.async_api import async_playwright
import statistics
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('URL')
PRICE_FILE = 'price_data.json'
SCRAPE_INTERVAL = 7200  # 2 hours

async def scrape_prices():
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(URL, timeout=120000, wait_until='networkidle')
            await page.click("button.ant-btn.css-7o12g0.ant-btn-primary.ant-btn-custom.ant-btn-custom-middle.ant-btn-custom-primary.bds-theme-component-light")
            await page.wait_for_selector("span.price-amount", timeout=120000)
            
            price_elements = await page.query_selector_all("span.price-amount")
            prices = [float((await element.inner_text()).split()[0].replace(',', '')) for element in price_elements[:10]]
            average_price = statistics.mean(prices)
            
            save_price(average_price)
            await browser.close()
            
        return average_price
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None

def save_price(price):
    data = {
        'price': price,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(PRICE_FILE, 'w') as f:
        json.dump(data, f)

def load_price():
    try:
        with open(PRICE_FILE, 'r') as f:
            data = json.load(f)
        saved_time = datetime.strptime(data['time'], "%Y-%m-%d %H:%M:%S")
        return data['price'], saved_time
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None, None
