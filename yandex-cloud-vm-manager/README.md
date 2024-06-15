# Yandex Cloud vm manager


## How to use
 - get yandex oauth token on https://oauth.yandex.ru/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb
 - fill .env file 
## Installation
 - install python 3.10
 - run python -m pip install -r requirements.txt
## Running
- Run python main.py

## .env Example
```
YANDEX_OAUTH_TOKEN=token
; in seconds. interval between checks
MONITORING_INTERVAL=10
```