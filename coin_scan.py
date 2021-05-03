import requests
import pandas as pd
import io


def get_coinmarketcap_df() -> pd.DataFrame:
    """
    get coin rank from coinmarketcap
    """
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?limit=400&sort=cmc_rank"
    headers = {"X-CMC_PRO_API_KEY": "06bfc722-65e8-4222-8f7c-d31b61d133ba"}
    res = requests.get(url, headers=headers).json()

    df = pd.DataFrame(res["data"])

    return df


def get_coinmarketcap_df2() -> pd.DataFrame:
    """
    get coin rank from coinmarketcap
    """
    url = (
        "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=400"
    )
    headers = {"X-CMC_PRO_API_KEY": "06bfc722-65e8-4222-8f7c-d31b61d133ba"}
    res = requests.get(url, headers=headers).json()

    df = pd.DataFrame(res["data"])

    return df


if __name__ == "__main__":
    cmc_df = get_coinmarketcap_df()
    df = cmc_df.dropna(subset=["platform"])

    df["platform"] = df["platform"].apply(lambda x: x["name"])

    print(df["platform"].value_counts())

    binance_chain = df[df["platform"].isin(["Binance Chain", "Binance Smart Chain"])]

    df2 = get_coinmarketcap_df2()
    tags = df2["tags"].explode().value_counts()
    is_defi = df2["tags"].apply(lambda x: "defi" in x)
    is_dot = df2["tags"].apply(lambda x: "dot-ecosystem" in x or "polkadot" in x)
    is_binance = df2["tags"].apply(
        lambda x: "binance-chain" in x
        or "binance-smart-chain" in x
        or "binance-launchpool" in x
    )
    is_exchange = df2["tags"].apply(lambda x: "decentralized-exchange" in x)
    is_collect = df2["tags"].apply(lambda x: "collectibles-nfts" in x)
    is_file = df2["tags"].apply(lambda x: "filesharing" in x)
    is_stable = df2["tags"].apply(lambda x: "stablecoin" in x)
    scaned = df2[is_defi & is_binance & ~is_collect & ~is_file & ~is_stable]
