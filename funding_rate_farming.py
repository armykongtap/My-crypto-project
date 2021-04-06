import config as cfg
from binance.client import Client
from binance.enums import ORDER_TYPE_LIMIT, SIDE_BUY, SIDE_SELL, TIME_IN_FORCE_GTC

client = Client(cfg.api_key, cfg.api_secret)

"""
Spot
"""


def buy_limit(symbol: str, price: float, volume: float) -> dict:
    print("Buy limit", symbol, price, volume)
    order = client.create_order(
        symbol=symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=volume,
        price=str(price),
    )
    return order


def sell_limit(symbol: str, price: float, volume: float) -> dict:
    print("Sell limit", symbol, price, volume)
    order = client.create_order(
        symbol=symbol,
        side=SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=volume,
        price=str(price),
    )
    return order


def get_orderbook_ticker(symbol: str) -> dict:
    ob = client.get_orderbook_ticker(symbol=symbol)
    return {
        "symbol": ob["symbol"],
        "bidPrice": float(ob["bidPrice"]),
        "bidQty": float(ob["bidQty"]),
        "askPrice": float(ob["askPrice"]),
        "askQty": float(ob["askQty"]),
    }


"""
Future
"""


def futures_long_limit(symbol: str, price: float, volume: float) -> dict:
    print("Long limit", symbol, price, volume)
    order = client.futures_create_order(
        symbol=symbol,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=volume,
        price=str(price),
    )
    return order


def futures_short_limit(symbol: str, price: float, volume: float) -> dict:
    print("Short limit", symbol, price, volume)
    order = client.futures_create_order(
        symbol=symbol,
        side=SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=volume,
        price=str(price),
    )
    return order


def futures_orderbook_ticker(symbol: str) -> dict:
    ob = client.futures_orderbook_ticker(symbol=symbol)
    return {
        "symbol": ob["symbol"],
        "bidPrice": float(ob["bidPrice"]),
        "bidQty": float(ob["bidQty"]),
        "askPrice": float(ob["askPrice"]),
        "askQty": float(ob["askQty"]),
    }


"""
Util
"""


def buy_and_short(symbol: str, volume: float, bypass_price_check: bool = False):
    spot_ob = get_orderbook_ticker(symbol=symbol)
    future_ob = futures_orderbook_ticker(symbol=symbol)

    if bypass_price_check or future_ob["bidPrice"] > spot_ob["askPrice"]:
        futures_short_limit(symbol=symbol, price=future_ob["bidPrice"], volume=volume)
        buy_limit(symbol=symbol, price=spot_ob["askPrice"], volume=volume)
    else:
        print("spot price higher than future")


def sell_and_long(symbol: str, volume: float, bypass_price_check: bool = False):
    spot_ob = get_orderbook_ticker(symbol=symbol)
    future_ob = futures_orderbook_ticker(symbol=symbol)

    if bypass_price_check or spot_ob["bidPrice"] > future_ob["askPrice"]:
        futures_long_limit(symbol=symbol, price=future_ob["bidPrice"], volume=volume)
        sell_limit(symbol=symbol, price=spot_ob["askPrice"], volume=volume)
    else:
        print("future price higher than spot")


if __name__ == "__main__":
    symbol = "DENTUSDT"
    volume = 1000

    buy_and_short(symbol=symbol, volume=volume)
    # sell_and_long(symbol=symbol, volume=volume, bypass_price_check=True)
