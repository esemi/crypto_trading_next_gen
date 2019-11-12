### Install

```sh
$ git clone git@github.com:esemi/crypto_trading_next_gen.git
$ cd crypto_trading_next_gen
$ virtualenv -p python3.8 venv
$ source venv/bin/activate
$ pip install -r requirements/common.txt 
$ cp configs/stage.env .env
```

### Run tests
```
pytest -s -v tests
```


### Run once
```
$ ./crypto_bot/trader.py
$ ./crypto_bot/supervisor.py
```


### Run like production
```
$ ./crypto_bot/trader.py
$ crontab crontab.txt
```
