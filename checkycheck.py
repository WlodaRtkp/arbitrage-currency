import yfinance as yf
import time
import requests
import pandas as pd
from datetime import datetime

# === CONFIG ===
TELEGRAM_TOKEN = "your_bot_token_here"
CHAT_ID = "your_chat_id_here"
CSV_LOG_FILE = "arbitrage_log.csv"
ARBITRAGE_THRESHOLD = 0.1  # percent
CHECK_INTERVAL = 60  # seconds

# === In-Memory Alert Cache ===
last_alerts = set()

# === Send Telegram Message ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# === Fetch Rate ===
def fetch_rate(pair):
    ticker = yf.Ticker(pair + "=X")
    data = ticker.history(period="1d", interval="1m")
    if data.empty:
        return None
    return data['Close'].iloc[-1]

# === Log to CSV ===
def log_to_csv(timestamp, triangle, rate1, rate2, rate3, profit):
    df = pd.DataFrame([{
        "timestamp": timestamp,
        "triangle": " → ".join(triangle),
        "rate1": rate1,
        "rate2": rate2,
        "rate3": rate3,
        "profit_percent": profit
    }])
    df.to_csv(CSV_LOG_FILE, mode='a', index=False, header=not pd.io.common.file_exists(CSV_LOG_FILE))

# === Arbitrage Check ===
def check_arbitrage_triangle(p1, p2, p3, base="EUR"):
    r1, r2, r3 = fetch_rate(p1), fetch_rate(p2), fetch_rate(p3)
    if None in (r1, r2, r3):
        print(f"⚠️ Could not fetch rates for: {p1}, {p2}, {p3}")
        return

    def normalize(pair, rate):
        return rate if pair.startswith(base) else 1 / rate

    a, b, c = normalize(p1, r1), normalize(p2, r2), normalize(p3, r3)
    result = a * b * c
    profit = (result - 1) * 100
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    alert_key = f"{p1}_{p2}_{p3}_{round(profit, 3)}"
    if profit > ARBITRAGE_THRESHOLD and alert_key not in last_alerts:
        last_alerts.add(alert_key)
        msg = (
            f"💰 *Arbitrage Opportunity Detected!*\n\n"
            f"*Pairs*: {p1}, {p2}, {p3}\n"
            f"*Rates*: {r1:.6f}, {r2:.6f}, {r3:.6f}\n"
            f"*Return*: {result:.6f} → *Profit*: {profit:.3f}%\n"
            f"*Time (UTC)*: {timestamp}"
        )
        send_telegram(msg)
        log_to_csv(timestamp, (p1, p2, p3), r1, r2, r3, profit)
        print(msg)
    else:
        print(f"No arbitrage: {p1}, {p2}, {p3} → {profit:.3f}%")

# === Triangles ===
triangles = [
    ("EURUSD", "USDJPY", "EURJPY"),
    ("EURGBP", "GBPUSD", "EURUSD"),
    ("GBPJPY", "JPYUSD", "GBPUSD")  # example extra triangle
]

# === Main Loop ===
if __name__ == "__main__":
    while True:
        print("\n🔍 Checking for arbitrage opportunities...")
        for t in triangles:
            check_arbitrage_triangle(*t)
        time.sleep(CHECK_INTERVAL)
