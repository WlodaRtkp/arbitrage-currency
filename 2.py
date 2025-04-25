import yfinance as yf
import time
import requests

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram error: {e}")

def fetch_rate(pair):
    ticker = yf.Ticker(pair + "=X")
    data = ticker.history(period="1d", interval="1m")
    if data.empty:
        return None
    return data['Close'].iloc[-1]

def check_arbitrage_triangle(p1, p2, p3, base="EUR"):
    r1 = fetch_rate(p1)
    r2 = fetch_rate(p2)
    r3 = fetch_rate(p3)

    if None in (r1, r2, r3):
        print(f"Could not fetch one of the pairs: {p1}, {p2}, {p3}")
        return

    print(f"Rates: {p1}={r1:.6f}, {p2}={r2:.6f}, {p3}={r3:.6f}")

    def rate(pair, r):
        return r if pair.startswith(base) else 1 / r

    a = rate(p1, r1)
    b = rate(p2, r2)
    c = rate(p3, r3)

    result = a * b * c
    profit = (result - 1) * 100

    if profit > 0.1:
        msg = (
            f"🔥 Arbitrage Opportunity Detected!\n"
            f"Triangle: {p1} → {p2} → {p3}\n"
            f"Rates: {p1}={r1:.6f}, {p2}={r2:.6f}, {p3}={r3:.6f}\n"
            f"Profit: {profit:.3f}%"
        )
        print(msg)
        send_telegram(msg)
    else:
        print(f"No arbitrage. Loop return: {result:.6f} ({profit:.3f}%)")

triangles = [
    ("EURUSD", "USDJPY", "EURJPY"),
    ("EURGBP", "GBPUSD", "EURUSD")
]

while True:
    print("\n--- Checking for arbitrage ---")
    for t in triangles:
        check_arbitrage_triangle(*t)
    time.sleep(60)
