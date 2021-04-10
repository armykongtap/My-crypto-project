import numpy as np
import pandas as pd

from binance.client import Client

client = Client()


def get_avg_funding_rate(days: int) -> pd.Series:
    fr_list = list()

    dt_range = (
        pd.date_range(
            end=pd.Timestamp.now(tz="UTC"), periods=days + 1, freq="D"
        ).astype(int)
        // 10 ** 6
    )

    for i in range(len(dt_range) - 1):
        fr_list += client.futures_funding_rate(
            startTime=str(dt_range[i]),
            endTime=str(dt_range[i + 1]),
            limit=1000,
        )

    df = pd.DataFrame(fr_list)

    df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms")
    df["fundingRate"] = df["fundingRate"].astype(np.float64)
    df = df.set_index("symbol")

    return df["fundingRate"].groupby(level=0).mean()


d = 5

print(f"Average {d} days of funding rate.")

avg_funding_rate = get_avg_funding_rate(days=d)
avg_funding_rate = avg_funding_rate.sort_values(ascending=False)

print(avg_funding_rate.head(5))
