import os
from dataclasses import dataclass
from typing import Callable, Union, Optional, Dict, List, Tuple
from decimal import getcontext, Decimal

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())


def _env(name: str, default=None, type_: Callable = str) -> Optional[Union[int, str, bool]]:
    var = os.getenv(name, default)

    if type_ is bool and var in ('True', 'true', '1'):
        var = True

    if type_ is bool and var in ('False', 'false', '0'):
        var = False

    if var is not None:
        var = type_(var)

    return var


TEST_MODE = _env('TEST_MODE', False, bool)
API_KEY = _env('API_KEY', '', str)
API_SECRET = _env('API_SECRET', '', str)
TICKER = 'ETHUSD'
COMPUTE_PRECISION = 6
getcontext().prec = COMPUTE_PRECISION


# Раз в сколько секунд проверяем свечи на вход
INIT_ORDER_TIME_OFFSET = 3600

# Раз в сколько секунд клирим старые ордера
CLEARING_TIME_OFFSET = 3600
# Время жизни ордера на бирже в секундах
CLEARING_ORDER_LIFETIME = 3600


@dataclass
class MinMaxFilter:
    min: float
    max: float


@dataclass
class CandleFilter:
    size: Optional[MinMaxFilter] = None  # Фильтр по % последней свечи от цены
    body: Optional[MinMaxFilter] = None  # Фильтр по % тела последней свечи


# Фильтры свечей на вход
@dataclass
class InitOrderConfig:
    take_profit_factor: float  # Множитель для размера свечи для тейк ордера
    clearing_interval: int = CLEARING_ORDER_LIFETIME  # секунд до клиринга
    first_candle: Optional[CandleFilter] = None
    second_candle: Optional[CandleFilter] = None
    last_candle: Optional[CandleFilter] = None


INIT_ORDER_FILTERS: List[InitOrderConfig] = [
    InitOrderConfig(take_profit_factor=4., clearing_interval=CLEARING_ORDER_LIFETIME * 2,
                    last_candle=CandleFilter(
                        size=MinMaxFilter(min=0.4, max=0.49),
                        body=MinMaxFilter(min=0.0, max=0.79)
                    ),
                    second_candle=CandleFilter(
                        body=MinMaxFilter(min=0.0, max=0.69)
                    ),
                    first_candle=CandleFilter(
                        body=MinMaxFilter(min=0.3, max=1.0)
                    )),
    InitOrderConfig(take_profit_factor=4.,
                    last_candle=CandleFilter(
                        size=MinMaxFilter(min=0.6, max=0.69),
                        body=MinMaxFilter(min=0.4, max=1.0),
                    ),
                    second_candle=CandleFilter(
                        body=MinMaxFilter(min=0.2, max=1.0)
                    ),
                    first_candle=CandleFilter(
                        body=MinMaxFilter(min=0.2, max=1.0)
                    )),
    InitOrderConfig(take_profit_factor=3.5, clearing_interval=CLEARING_ORDER_LIFETIME * 2,
                    last_candle=CandleFilter(
                        size=MinMaxFilter(min=0.7, max=0.79),
                        body=MinMaxFilter(min=0.1, max=0.79),
                    )),
    InitOrderConfig(take_profit_factor=4.,
                    last_candle=CandleFilter(
                        size=MinMaxFilter(min=0.8, max=0.89),
                        body=MinMaxFilter(min=0.3, max=0.69),
                    ),
                    second_candle=CandleFilter(
                        body=MinMaxFilter(min=0.0, max=0.69)
                    ),
                    first_candle=CandleFilter(
                        body=MinMaxFilter(min=0.3, max=0.69)
                    )),
    InitOrderConfig(take_profit_factor=4.,
                    last_candle=CandleFilter(
                        size=MinMaxFilter(min=1.6, max=1.99),
                        body=MinMaxFilter(min=0.1, max=1.0),
                    )),
    InitOrderConfig(take_profit_factor=4.,
                    last_candle=CandleFilter(
                        size=MinMaxFilter(min=0.5, max=0.55),
                        body=MinMaxFilter(min=0.3, max=1.0),
                    ),
                    second_candle=CandleFilter(
                        body=MinMaxFilter(min=0.5, max=1.0)
                    ),
                    first_candle=CandleFilter(
                        body=MinMaxFilter(min=0.0, max=0.59)
                    )),
]

# Отступ в долларах от цены свечи для ордера на вход в сделку (триггерная цена)
INIT_ORDER_TRIGGER_PRICE_OFFSET = 0.05
# Отступ в долларах от цены свечи для ордера на вход в сделку (цена ордера)
INIT_ORDER_PRICE_OFFSET = 0.1
# Отступ в долларах от цены свечи для стоп-ордера
STOP_ORDER_PRICE_OFFSET = 0.
# Отступ в долларах от цены свечи для тейк-ордера
TAKE_ORDER_PRICE_OFFSET = 0.1

# Размер ордера на вход в сделку, в BTC. Считается как 1% от депо в битках.
INIT_ORDER_SIZE_IN_BTC = _env('INIT_ORDER_SIZE_IN_BTC', None, Decimal)  # todo change for production

RED_COLOR = 'RED'
GREEN_COLOR = 'GREEN'
LIMIT_CALL_TRIES = 20
LIMIT_CALL_TIMEOUT = 5
