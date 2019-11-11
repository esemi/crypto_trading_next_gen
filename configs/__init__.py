import os
from typing import Callable, Union, Optional

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())


def _env(name: str, type_: Callable = str) -> Optional[Union[int, str, bool]]:
    var = os.getenv(name)

    if type_ is bool and var in ('True', 'true', '1'):
        var = True

    if type_ is bool and var in ('False', 'false', '0'):
        var = False

    if var is not None:
        var = type_(var)

    return var


API_HOST = _env('EXCHANGE_API_HOST')