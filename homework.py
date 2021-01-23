import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG, filename='main.log', filemode='w')

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HEADERS = {
    'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'
}
URL = os.getenv('URL')
HOMEWORK_STATUS_DICT = {
    'reviewing': 'Работа взята в ревью',
    'approved': 'Ревьюеру всё понравилось, можно приступать к следующему '
                'уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.'
}


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_STATUS_DICT:
        msg = f'Неизвестный статус состояния работы {homework_name}.'
        logging.info(msg)
        return msg
    verdict = HOMEWORK_STATUS_DICT.get(status)
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(URL, params=params, headers=HEADERS)
        return homework_statuses.json()
    except requests.RequestException as error:
        logging.error(error, exc_info=True)


def send_message(msg, bot_client):
    logging.info('Отправка выполнена')
    return bot_client.send_message(chat_id=CHAT_ID, text=msg)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)
        except Exception as error:
            print(f'Бот столкнулся с ошибкой: {error}')
            time.sleep(5)


if __name__ == '__main__':
    main()
