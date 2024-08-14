from flask import Flask, jsonify
from scraper import scrape_prices, load_price
from datetime import datetime
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()
app = Flask(__name__)
SCRAPE_INTERVAL = 7200  # 2 hours

@app.route('/api/price', methods=['GET'])
def get_price():
    price, saved_time = load_price()
    if price is None or (datetime.now() - saved_time).total_seconds() > SCRAPE_INTERVAL:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        price = loop.run_until_complete(scrape_prices())
        loop.close()
    return jsonify({
        'price': price,
        'timestamp': saved_time.isoformat() if saved_time else None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
