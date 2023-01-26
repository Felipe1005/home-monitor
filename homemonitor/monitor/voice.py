from . import models
from .timeout import timeout
from twilio.rest import Client

config = models.Config.objects.filter(id=1).values()[0]

origin_path = config['origin_path']
aux_path = config['aux_path']
final_path = config['final_path']



def notificate_client(monitor, channel, client):
    active = channel.active
    account_sid = channel.twilio_account_sid
    auth_token = channel.twilio_auth_token
    from_number = channel.twilio_from_number
    from_number = '+' + str(from_number)
    message = channel.message
    user_name = client.name
    to_number = client.phone
    to_number = '+' + str(to_number)
    monitor_name = monitor.name
    text_message = message.replace('{{USER_NAME}}', user_name)
    text_message = text_message.replace('{{MONITOR_NAME}}', monitor_name)
    if active:
        client = Client(account_sid, auth_token)
        try:
            call = client.calls.create(
                            twiml='<Response><Say voice="Polly.Mia-Neural" language="es-MX">' + text_message + '</Say></Response>',
                            to=to_number,
                            from_=from_number
                            )
            print('Llamada de notificación realizada correctamente')
            return True
        except Exception:
            print('Fallo en intento de llamada de notificación')
            return False


