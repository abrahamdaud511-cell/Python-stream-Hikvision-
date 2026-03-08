import numpy as np
import pandas as pd
import datetime

def simulate_btc_prices(days=60, initial_price=50000, volatility=0.04, drift=0.0005):
    """
    Simulates Bitcoin price data using Geometric Brownian Motion.
    volatility: daily volatility (standard deviation of returns)
    drift: expected daily return
    """
    np.random.seed(42)  # For reproducibility
    returns = np.random.normal(drift, volatility, days)
    price_path = initial_price * np.exp(np.cumsum(returns))

    # Prepend the initial price to have 61 data points (including Day 0)
    # or just use the 60 days as requested.
    # Let's generate 90 days of data and only look at the last 60 for the ledger,
    # to ensure MAs are calculated from the start of our 60-day window.
    # Actually, the prompt says "simulates 60 days", so I'll simulate 90 and use the last 60
    # so that the 30-day MA is available from day 1 of our ledger.

    total_days = days + 30
    returns = np.random.normal(drift, volatility, total_days)
    prices = initial_price * np.exp(np.cumsum(returns))

    dates = [datetime.date.today() - datetime.timedelta(days=total_days - i) for i in range(total_days)]

    df = pd.DataFrame({'Date': dates, 'Price': prices})
    return df

def run_trading_simulation(df):
    # Calculate Moving Averages
    df['MA7'] = df['Price'].rolling(window=7).mean()
    df['MA30'] = df['Price'].rolling(window=30).mean()

    # Trim to the last 60 days as requested
    df = df.tail(60).reset_index(drop=True)

    # Portfolio initial state
    usd_balance = 10000.0
    btc_balance = 0.0
    position = None  # None, 'Long'

    print(f"{'Date':<12} | {'Price':<10} | {'MA7':<10} | {'MA30':<10} | {'Action':<10} | {'Portfolio (USD Equivalent)':<15}")
    print("-" * 85)

    initial_total_value = usd_balance

    for i in range(len(df)):
        row = df.iloc[i]
        date_str = str(row['Date'])
        price = row['Price']
        ma7 = row['MA7']
        ma30 = row['MA30']

        action = "HOLD"

        # Golden Cross Strategy Logic
        # Buy if MA7 > MA30 and we don't have BTC
        if ma7 > ma30 and position != 'Long':
            # Buy
            btc_balance = usd_balance / price
            usd_balance = 0
            position = 'Long'
            action = "BUY"
        # Sell (Death Cross) if MA7 < MA30 and we have BTC
        elif ma7 < ma30 and position == 'Long':
            # Sell
            usd_balance = btc_balance * price
            btc_balance = 0
            position = None
            action = "SELL"

        current_value = usd_balance + (btc_balance * price)
        print(f"{date_str:<12} | {price:10.2f} | {ma7:10.2f} | {ma30:10.2f} | {action:<10} | {current_value:15.2f}")

    final_value = usd_balance + (btc_balance * df.iloc[-1]['Price'])
    roi = ((final_value - initial_total_value) / initial_total_value) * 100

    print("-" * 85)
    print(f"Final Portfolio Performance:")
    print(f"Starting Balance: ${initial_total_value:,.2f}")
    print(f"Ending Balance:   ${final_value:,.2f}")
    print(f"Total ROI:        {roi:.2f}%")

if __name__ == "__main__":
    # Simulate 60 days (plus 30 for buffer)
    btc_df = simulate_btc_prices(days=60)
    run_trading_simulation(btc_df)
