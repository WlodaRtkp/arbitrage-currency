import yfinance as yf
import time

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

    # Normalize direction
    def rate(pair, r):
        if pair.startswith(base):
            return r
        else:
            return 1 / r

    a = rate(p1, r1)
    b = rate(p2, r2)
    c = rate(p3, r3)

    result = a * b * c
    profit = (result - 1) * 100

    if profit > 0.1:
        print(f"🔥 Arbitrage Opportunity: Profit = {profit:.3f}%")
    else:
        print(f"No arbitrage. Loop return: {result:.6f} ({profit:.3f}%)")

# Loop over two triangles
triangles = [
    ("EURUSD", "USDJPY", "EURJPY"),
    ("EURGBP", "GBPUSD", "EURUSD")
]

while True:
    print("\n--- Checking for arbitrage ---")
    for t in triangles:
        check_arbitrage_triangle(*t)
    time.sleep(60)
