import time
from statistics import mean

import pandas as pd
from binance.client import Client

client = Client()


def get_all_tickers() -> pd.Series:
    ticker = client.get_all_tickers()
    df = pd.DataFrame(ticker)
    df = df.set_index("symbol")
    return df["price"].astype(float)


def futures_symbol_ticker() -> pd.Series:
    ticker = client.futures_symbol_ticker()
    df = pd.DataFrame(ticker)
    df = df.set_index("symbol")
    return df["price"].astype(float)


def get_premium() -> pd.Series:
    spot = get_all_tickers()
    future = futures_symbol_ticker()
    premium = future / spot
    premium = premium.dropna()
    return premium


symbol = input("Symbol : ")
print(f"Premium Index : {symbol}")

l = list()

for i in range(5):
    premium = get_premium().sort_values(ascending=False)
    p = premium.loc[symbol]
    print(p)
    l.append(p)
    time.sleep(10)

print(f"Average : {mean(l)}")
