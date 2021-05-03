import pandas as pd
import requests
from bs4 import BeautifulSoup

from binance.client import Client
from binance.enums import (
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL,
    TIME_IN_FORCE_GTC,
)

bn_client = Client()


def get_exchange_rate(symbol: str) -> float:
    url = f"https://finance.yahoo.com/quote/USDTHB=X?ltr=1"
    res = requests.request("GET", url)

    soup = BeautifulSoup(res.text, "html.parser")

    return float(
        soup.find("span", class_="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)").text
    )


def bitkub_price() -> pd.Series:
    url = f"https://api.bitkub.com/api/market/ticker"

    res = requests.get(url)

    df = pd.DataFrame(res.json())

    df = df.T
    df.index = df.index.str[4:] + "USDT"

    price = df["last"]
    price.name = "price"
    price = price / USDTHB

    return price


def binance_price() -> pd.Series:
    ticker = bn_client.get_all_tickers()
    df = pd.DataFrame(ticker)
    df = df.set_index("symbol")
    return df["price"].astype(float)


def get_premium() -> pd.Series:
    ex1 = bitkub_price()
    ex2 = binance_price()

    premium = ex1 / ex2
    premium = premium.dropna()
    premium = premium.sort_values(ascending=False)

    return premium


USDTHB = get_exchange_rate(symbol="USDTHB")

if __name__ == "__main__":
    print("Premium between BitKub and Binance")
    premium = get_premium()
    print(premium.head(10))

