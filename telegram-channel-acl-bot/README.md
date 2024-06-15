# Telegram channel acl bot

# !!!Bot can't write first!!!

## How to use
 - create bot via @BotFather, obtain TELEGRAM_TOKEN
 - open https://my.telegram.org/ and obtain api_id & api_hash
 - obtain channel id: https://api.telegram.org/bot{BOT_TOKEN}/getUpdates
 - fill employees file with tg user ids(can get via @userinfobot). 1 id = 1 line
 - fill .env file 
## Installation
 - install python 3.10
 - run python -m pip install -r requirements.txt
## Running
- Run python main.py

## .env Example
```
TELEGRAM_TOKEN="token from @botfather"
TELEGRAM_CHANNEL_ID=-1002215748140
; space between ids. you can get your id from @userinfobot
TELEGRAM_ADMIN_IDS=123 221 1277
API_ID=12345678
API_HASH=29aa0aa0a00a0a0000aaaaaa00a0a00a
; in seconds. interval between checks
CHECK_INTERVAL=5
```