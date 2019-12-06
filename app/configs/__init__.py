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
TICKER = _env('TICKER', None, str)

# Отступ в долларах от цены свечи для ордера на вход в сделку
INIT_ORDER_PRICE_OFFSET = 1.
# Отступ в долларах от цены свечи для стоп-ордера
STOP_ORDER_PRICE_OFFSET = 2.

# Размер ордера на вход в сделку, в BTC. Считается как 1% от депо в битках.
INIT_ORDER_SIZE_IN_BTC = _env('INIT_ORDER_SIZE_IN_BTC', None, float)  # todo change for production

RED_COLOR = 'RED'
GREEN_COLOR = 'GREEN'
LIMIT_CALL_TRIES = 5
LIMIT_CALL_TIMEOUT = 5
