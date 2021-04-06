import numpy as np
import pandas as pd

from binance.client import Client

client = Client()


def get_avg_funding_rate(symbol: str, limit: int = 30) -> float:
    funding_rate = client.futures_funding_rate(symbol=symbol, limit=str(limit))
    df = pd.DataFrame(funding_rate)
    df["fundingRate"] = df["fundingRate"].astype(np.float64)
    return df["fundingRate"].mean()


def get_futures_exchange_info() -> pd.DataFrame:
    info = client.futures_exchange_info()
    df = pd.DataFrame(info["symbols"])
    return df


future_info = get_futures_exchange_info()
future_info = future_info[future_info["contractType"] == "PERPETUAL"]

avg_funding_rate = future_info["symbol"].apply(get_avg_funding_rate)
avg_funding_rate.index = future_info["symbol"]

avg_funding_rate = avg_funding_rate.sort_values(ascending=False)

print(avg_funding_rate.head(10))
