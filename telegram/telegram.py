import time
import requests
import logging

class botTelegram():

    def __init__(self, bot_token, bot_chatID):
        self.bot_token = bot_token
        self.bot_chatID = bot_chatID
    

    def telegram_bot_sendtext(self, bot_message):

        send_text = 'https://api.telegram.org/bot' + self.bot_token + '/sendMessage?chat_id=' + self.bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()
