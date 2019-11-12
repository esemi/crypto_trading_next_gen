import warnings

from configs import TEST_MODE

warnings.filterwarnings("ignore")
client = None


def init_client(test_mode: bool):
    import bitmex
    global client
    client = bitmex.bitmex(test=test_mode)


def get_buckets(ticker: str, count: int) -> list:
    return client.Trade.Trade_getBucketed(binSize='1h', partial=False, symbol=ticker, count=count,
                                          reverse=True).result()[0]


init_client(TEST_MODE)
