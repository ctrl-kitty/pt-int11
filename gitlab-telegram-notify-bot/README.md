# Gitlab Telegram notify bot

# !!!Bot can't write first!!!

## How to use
 - obtain gitlab token on https://gitlab.com/-/user_settings/personal_access_tokens with api, read_api
rights
 - if you use private gitlab server, change GITLAB_URL in .env
 - create bot via @BotFather, obtain TELEGRAM_TOKEN
 - fill .env file
## Installation
 - install python 3.10
 - run python -m pip install -r requirements.txt
## Running
- Run python main.py

## .env Example
```
GITLAB_TOKEN="glpat-AAAAAAAAAAAAAAAAAAAA"
GITLAB_URL="https://gitlab.com/api/v4"
GITLAB_PROJECT_ID=12345678
TELEGRAM_TOKEN="token from @botfather"
; space between ids. you can get your id from @userinfobot
TELEGRAM_CHAT_IDS=123 221 1277
; in seconds. notification interval
NOTIFICATION_TIMEOUT=5
```