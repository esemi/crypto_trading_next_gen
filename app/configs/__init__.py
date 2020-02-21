import os
from typing import Callable, Union, Optional

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

# Раз в сколько секунд проверяем свечи на вход
INIT_ORDER_TIME_OFFSET = 3600

# Раз в сколько секунд клирим старые ордера
CLEARING_TIME_OFFSET = 3600
# Время жизни ордера на бирже в секундах
CLEARING_ORDER_LIFETIME = 3600


# Фильтры свечи на вход
# List[
#   Tuple(
#       Tuple(float, float),  # Фильтр по % свечи от цены
#       Tuple(float, float),  # Фильтр по % тела свечи
#       int,                  # секунд до клиринга
#       float,                # Множитель для размера свечи для тейк ордера
#   )
# ]
INIT_ORDER_FILTERS = [
    ((0.4, 0.49), (0., 0.69), CLEARING_ORDER_LIFETIME * 2, 4.),
    ((0.6, 0.69), (0.4, 1.0), CLEARING_ORDER_LIFETIME, 4.),
    ((0.7, 0.79), (0.2, 1.0), CLEARING_ORDER_LIFETIME * 2, 3.5),
    ((0.8, 0.89), (0.3, 0.69), CLEARING_ORDER_LIFETIME, 4.),
    ((0.9, 0.99), (0., 0.49), CLEARING_ORDER_LIFETIME, 3.5),
    ((1.6, 1.99), (0.1, 1.0), CLEARING_ORDER_LIFETIME, 4.),
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
INIT_ORDER_SIZE_IN_BTC = _env('INIT_ORDER_SIZE_IN_BTC', None, float)  # todo change for production

RED_COLOR = 'RED'
GREEN_COLOR = 'GREEN'
LIMIT_CALL_TRIES = 20
LIMIT_CALL_TIMEOUT = 5
