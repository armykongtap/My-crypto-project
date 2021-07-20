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


def get_p2p_biance_price(
    asset: str = "BUSD", fait: str = "THB", tradeType: str = "SELL"
) -> float:
    url = "https://c2c.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    json = {
        "page": 1,
        "rows": 1,
        "payTypes": [],
        "asset": asset,
        "tradeType": tradeType,
        "fiat": fait,
        "publisherType": None,
        "merchantCheck": False,
    }
    res = requests.post(url, json=json)
    out = float(res.json()["data"][0]["adv"]["price"])
    return out


def bitkub_price() -> pd.Series:
    url = "https://api.bitkub.com/api/market/ticker"

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

    return premium


def get_withdraw_fee() -> pd.Series:
    res = bn_client.get_asset_details()
    df = pd.DataFrame(res["assetDetail"]).T
    df.index.name = "symbol"

    df.index += "USDT"

    df["price"] = binance_price()

    df["withdrawFee"] *= df["price"]

    return df["withdrawFee"].dropna()


USDTHB = get_p2p_biance_price()

if __name__ == "__main__":
    print("Premium between BitKub and Binance")
    premium = get_premium().sort_values(ascending=False).to_frame()
    premium["withdrawFee"] = get_withdraw_fee()

    premium = premium[premium["withdrawFee"] < 10]

    print(premium.head(10))
