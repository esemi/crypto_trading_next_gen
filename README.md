Trading bot for crypto exchanges [![Deploy](https://github.com/esemi/crypto_trading_next_gen/actions/workflows/deployment.yml/badge.svg?branch=master)](https://github.com/esemi/crypto_trading_next_gen/actions/workflows/deployment.yml)
---

### Install

```sh
$ git clone git@github.com:esemi/crypto_trading_next_gen.git
$ cd crypto_trading_next_gen
$ virtualenv -p python3.8 venv
$ source venv/bin/activate
$ pip install -r requirements/common.txt 
$ cp configs/stage.env .env
```

### Tests
```
pytest -s -v tests
```


### Run local
```
$ ./app/trader.py --debug=True
```


### Run on production
@see [etc/*.conf](https://github.com/esemi/crypto_trading_next_gen/blob/master/etc/)

