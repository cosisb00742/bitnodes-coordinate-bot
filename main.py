import requests
import time
import os
import threading
from collections import defaultdict
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = "https://bitnodes.io/api/v1/snapshots/latest/"
CHECK_INTERVAL = 300  # seconds (5 minutes)
THRESHOLD_PERCENT = 10

previous_coords = defaultdict(int)

# Mapping locations to coins
location_coin_map = {
    "Germany": "BTC",
    "United States": "SOL",
    "Singapore": "ETH",
    "Japan": "XRP",
    "France": "BNB",
    "South Korea": "DOGE"
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Telegram Error:", e)

def analyze_and_alert():
    global previous_coords
    while True:
        try:
            response = requests.get(API_URL)
            if response.status_code != 200:
                time.sleep(CHECK_INTERVAL)
                continue

            data = response.json()
            nodes = data.get("nodes", {})

            current_coords = defaultdict(int)
            for node in nodes.values():
                geo = node[7]
                if geo:
                    country = geo.get("country")
                    if country:
                        current_coords[country] += 1

            for country, count in current_coords.items():
                previous_count = previous_coords[country]
                if previous_count == 0:
                    continue

                percent_change = ((count - previous_count) / previous_count) * 100
                if abs(percent_change) >= THRESHOLD_PERCENT:
                    coin = location_coin_map.get(country, "BTC")
                    sentiment = "Bullish 🚀" if percent_change > 0 else "Bearish 📉"
                    action = "LONG / BUY" if percent_change > 0 else "SHORT / SELL"

                    msg = (
                        f"⚡ Bitnodes Geo Spike Detected!
"
                        f"📍 Location: {country}
"
                        f"{'📈' if percent_change > 0 else '📉'} Node Change: {percent_change:.2f}%
"
                        f"🪙 Affected Coin: {coin}
"
                        f"Sentiment: {sentiment}
"
                        f"Suggested Action: {action}"
                    )
                    send_telegram_message(msg)

            previous_coords = current_coords
        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    t = threading.Thread(target=analyze_and_alert)
    t.start()
