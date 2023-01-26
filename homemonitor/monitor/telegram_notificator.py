import telegram
from . import models

config = models.Config.objects.filter(id=1).values()[0]

origin_path = config['origin_path']
aux_path = config['aux_path']
final_path = config['final_path']

def notificate_client(monitor, channel, client, screenshot_file_name):
    active = channel.active
    telegram_key = channel.telegram_key
    message = channel.message
    telegram_chat_id = client.telegram_chat_id
    user_name = client.name
    monitor_name = monitor.name
    text_message = message.replace('{{USER_NAME}}', user_name)
    text_message = text_message.replace('{{MONITOR_NAME}}', monitor_name)
    if active:
        try:
            bot =  telegram.Bot(telegram_key)
            bot.send_message(text=text_message, chat_id= telegram_chat_id)
            screenshot_path = final_path + '/' + screenshot_file_name
            screenshot = open(screenshot_path, 'rb')
            bot.send_photo(photo = screenshot, chat_id= telegram_chat_id)
            print('Notificación por telegram realizada correctamente')
            return True
        except Exception:
            print('Fallo en intento de notificar por telegram')
            return False

