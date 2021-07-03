import pandas as pd
import requests
from binance.client import Client
from binance.enums import (
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL,
    TIME_IN_FORCE_GTC,
)
from bs4 import BeautifulSoup

import config as cfg

# bn_client = Client()
bn_client = Client(cfg.api_key, cfg.api_secret)


def bitkub_price() -> pd.Series:
    url = f"https://api.bitkub.com/api/market/ticker"

    res = requests.get(url)

    df = pd.DataFrame(res.json())

    df = df.T
    df.index = df.index.str[4:] + "USDT"

    price = df["last"]
    price.name = "price"
    price = price / price["USDTUSDT"]

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

    return premium


def get_withdraw_fee() -> pd.Series:
    res = bn_client.get_asset_details()
    df = pd.DataFrame(res["assetDetail"]).T
    df.index.name = "symbol"

    df.index += "USDT"

    df["price"] = binance_price()

    df["withdrawFee"] *= df["price"]

    return df["withdrawFee"].dropna()


if __name__ == "__main__":
    print("Premium between BitKub and Binance")
    premium = get_premium().sort_values(ascending=False).to_frame()
    premium["withdrawFee"] = get_withdraw_fee()

    premium = premium[premium["withdrawFee"] < 10]

    print(premium.head(5))
    print(premium.tail(5))

