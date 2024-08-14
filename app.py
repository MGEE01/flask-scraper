from flask import Flask, jsonify
from scraper import scrape_prices, load_price
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv

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
        if price is None:
            return jsonify({'error': 'Failed to scrape price'}), 500
    return jsonify({
        'price': price,
        'timestamp': saved_time.isoformat() if saved_time else None
    })

if __name__ == '__main__':
    from gunicorn.app.base import BaseApplication
    
    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
        
        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)
        
        def load(self):
            return self.application
    
    options = {
        'bind': '%s:%s' % ('0.0.0.0', os.environ.get('PORT', '5000')),
        'workers': 1,
    }
    StandaloneApplication(app, options).run()
