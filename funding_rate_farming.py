from dataclasses import dataclass
from threading import Timer
from typing import Callable

from binance.client import Client
from binance.enums import (
    ORDER_TYPE_LIMIT,
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL,
    TIME_IN_FORCE_GTC,
)
from binance.websockets import BinanceSocketManager

import config as cfg

# client = Client(cfg.api_key, cfg.api_secret)
client = Client()
bm = BinanceSocketManager(client)


@dataclass
class OrderBook:
    best_bid: float = None
    best_ask: float = None


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


def buy_market(symbol: str, volume: float) -> dict:
    print("Buy market", symbol, volume)
    order = client.create_order(
        symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=volume,
    )
    return order


def sell_market(symbol: str, volume: float) -> dict:
    print("Sell market", symbol, volume)
    order = client.create_order(
        symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=volume,
    )
    return order


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


def futures_long_market(symbol: str, volume: float) -> dict:
    print("Long market", symbol, volume)
    order = client.futures_create_order(
        symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=volume,
    )
    return order


def futures_short_market(symbol: str, volume: float) -> dict:
    print("Short market", symbol, volume)
    order = client.futures_create_order(
        symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=volume,
    )
    return order


"""
Stream
"""


def sub_symbol_ticker_socket(symbol: str, trigger_func: Callable) -> OrderBook:
    ob = OrderBook()

    def process_message(msg):
        if ob.best_bid == float(msg["b"]) and ob.best_ask == float(msg["a"]):
            return
        ob.best_bid = float(msg["b"])
        ob.best_ask = float(msg["a"])
        trigger_func()

    conn_key = bm.start_symbol_ticker_socket(symbol, process_message)
    print(f"Subscribe Spot: {conn_key}")

    return ob


def sub_symbol_ticker_futures_socket(symbol: str, trigger_func: Callable) -> OrderBook:
    ob = OrderBook()

    def process_message(msg):
        if ob.best_bid == float(msg["data"]["b"]) and ob.best_ask == float(
            msg["data"]["a"]
        ):
            return
        ob.best_bid = float(msg["data"]["b"])
        ob.best_ask = float(msg["data"]["a"])
        trigger_func()

    conn_key = bm.start_symbol_ticker_futures_socket(symbol, process_message)
    print(f"Subscribe Future: {conn_key}")

    return ob


"""
Util
"""


def buy_and_short(symbol: str, volume: float):
    buy_market(symbol=symbol, volume=volume)
    futures_short_market(symbol=symbol, volume=volume)


def sell_and_long(symbol: str, volume: float):
    sell_market(symbol=symbol, volume=volume)
    futures_long_market(symbol=symbol, volume=volume)


def sub_premium_buy(
    symbol: str,
    min_premium: float,
    trigger_func: Callable,
    args: list = list(),
    kwargs: dict = dict(),
):
    def check_premium():
        try:
            premium = future_ob.best_bid / spot_ob.best_ask - 1
        except TypeError as e:
            print(e)
            return
        print(f"Premium {premium:.8f}")
        if premium > min_premium:
            bm.close()
            trigger_func(*args, **kwargs)

    spot_ob = sub_symbol_ticker_socket(symbol=symbol, trigger_func=check_premium)
    future_ob = sub_symbol_ticker_futures_socket(
        symbol=symbol, trigger_func=check_premium
    )
    bm.start()


def sub_premium_sell(
    symbol: str,
    max_premium: float,
    trigger_func: Callable,
    args: list = list(),
    kwargs: dict = dict(),
):
    def check_premium():
        try:
            premium = future_ob.best_ask / spot_ob.best_bid - 1
        except TypeError as e:
            print(e)
            return
        print(f"Premium {premium:.8f}")
        if premium < max_premium:
            bm.close()
            trigger_func(*args, **kwargs)

    spot_ob = sub_symbol_ticker_socket(symbol=symbol, trigger_func=check_premium)
    future_ob = sub_symbol_ticker_futures_socket(
        symbol=symbol, trigger_func=check_premium
    )
    bm.start()


if __name__ == "__main__":
    symbol = "BTTUSDT"
    volume = 100

    sub_premium_buy(
        symbol=symbol,
        min_premium=0.002,
        trigger_func=buy_and_short,
        kwargs={"symbol": symbol, "volume": volume},
    )

    # sub_premium_sell(
    #     symbol=symbol,
    #     max_premium=0.001,
    #     trigger_func=sell_and_long,
    #     kwargs={"symbol": symbol, "volume": volume},
    # )

    Timer(interval=60, function=bm.close).start()
