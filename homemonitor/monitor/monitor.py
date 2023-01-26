from . import models, azure_backend, telegram_notificator, voice
from django.utils import timezone
import datetime
import requests
import os
import cv2
import threading
# import ffmpeg

config = models.Config.objects.filter(id=1).values()[0]

origin_path = config['origin_path']
aux_path = config['aux_path']
final_path = config['final_path']


# bufferless VideoCapture
class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    # grab frames as soon as they are available
    def _reader(self):
        while True:
            with self.lock:
                ret = self.cap.grab()
            if not ret:
                break

    # retrieve latest frame
    def read(self):
        with self.lock:
            _, frame = self.cap.retrieve()
        return frame



def get_observers(monitor_key):
    valid_observers = list()
    observers = models.Observer.objects.all()
    for observer in observers:
        monitors = observer.monitors.values()
        for monitor in monitors:
            if monitor['monitor_key'] == monitor_key:
                valid_observers.append(observer)
                break
    return(valid_observers)


def get_screenshot_from_monitor(monitor_key):
    origin_https = False
    monitor = models.Monitor.objects.filter(monitor_key=monitor_key)
    origin_id = monitor.values()[0]['origin_id']
    origin = models.Origin.objects.filter(id=origin_id)
    api_key = origin.values()[0]['api_key']
    group_key = origin.values()[0]['group_key']
    origin_ip_address =  origin.values()[0]['origin_ip_address']
    origin_port =  origin.values()[0]['origin_port']
    if origin_https:
        stt = 'https://'
    else:
        stt = 'http://'
    url_options = {
        'screenshot': '/jpeg/',
        'monitor': '/monitor/',
        'mp4': '/mp4/'
    }
    screenshot_url = stt + origin_ip_address + ':' + str(origin_port) + '/' + api_key + url_options['screenshot'] + group_key + '/' + monitor_key + '/s.jpg'
    mp4_url = stt + origin_ip_address + ':' + str(origin_port) + '/' + api_key + url_options['mp4'] + group_key + '/' + monitor_key + '/s.mp4'
    screenshot = requests.get(screenshot_url)
    now = timezone.localtime(timezone.now()).strftime('%Y-%m-%d__%H-%M-%S')
    screenshot_file_name = 's-' + now + '.jpg'
    screenshot_path = origin_path + '/' + screenshot_file_name
    file = open(screenshot_path, 'wb')
    file.write(screenshot.content)
    file.close()
    return screenshot_file_name

def get_screenshot_from_monitor2(monitor_key):
    origin_https = False
    monitor = models.Monitor.objects.filter(monitor_key=monitor_key)
    origin_id = monitor.values()[0]['origin_id']
    origin = models.Origin.objects.filter(id=origin_id)
    api_key = origin.values()[0]['api_key']
    group_key = origin.values()[0]['group_key']
    origin_ip_address =  origin.values()[0]['origin_ip_address']
    origin_port =  origin.values()[0]['origin_port']
    if origin_https:
        stt = 'https://'
    else:
        stt = 'http://'
    url_options = {
        'screenshot': '/jpeg/',
        'monitor': '/monitor/',
        'mp4': '/mp4/'
    }
    screenshot_url = stt + origin_ip_address + ':' + str(origin_port) + '/' + api_key + url_options['screenshot'] + group_key + '/' + monitor_key + '/s.jpg'
    mp4_url = stt + origin_ip_address + ':' + str(origin_port) + '/' + api_key + url_options['mp4'] + group_key + '/' + monitor_key + '/s.mp4'
    vc = VideoCapture(mp4_url)
    screenshot = vc.read()
    now = timezone.localtime(timezone.now()).strftime('%Y-%m-%d__%H-%M-%S')
    screenshot_file_name = 's-' + now + '.jpg'
    screenshot_path = origin_path + '/' + screenshot_file_name
    file = open(screenshot_path, 'wb')
    file.write(screenshot.content)
    file.close()
    return screenshot_file_name

def process_movement(monitor_key):
    monitor = models.Monitor.objects.filter(monitor_key=monitor_key)[0]
    observers = get_observers(monitor_key)
    now = timezone.now()
    now_local = timezone.localtime(now)
    current_hour = now_local.strftime('%H')
    current_day = now_local.strftime('%d')
    current_week_day = now_local.weekday()
    last_trigger = monitor.last_trigger
    timeout = monitor.timeout
    delta_time = now - last_trigger
    delta_time = delta_time.seconds / 60.0
    print('Movimiento detectado en ' + monitor.name + ' a las ' + str(current_hour) + ' horas. Se validara si corresponde a persona(s)')
    print('Deltatime = ' + str(delta_time))
    print('Timeout = ' + str(timeout))
    for observer in observers:
        schedules = observer.schedule.values()
        for schedule in schedules:  
            schedule_days = [int(a) for a in schedule['days'].split(',')]
            schedule_hours = [int(a) for a in schedule['hours'].split(',')]
            if (observer.schedule_off or (int(current_hour) in schedule_hours and current_week_day in schedule_days)) and (delta_time > timeout):
                screenshot_file_name = get_screenshot_from_monitor(monitor_key)
                backends = observer.backends.values()
                for backend in backends:
                    backend_response = False
                    # screnshot_path = origin_path + '/' + screenshot_file_name
                    if backend['active']:
                        print('Se pregunta a Azure Cognitive Service si corresponde a persona')
                        try:
                            result = azure_backend.analyze_image(backend, screenshot_file_name)
                            backend_response = True
                            persons = azure_backend.get_persons(result)
                        except Exception:
                            persons = list()

                        if len(persons) > 0 and backend_response:
                            azure_backend.draw_rectangle(persons, screenshot_file_name)
                            print('Persona detectada en el ' + monitor.name + ', se debe notificar')
                            event = models.Event(event_datetime = now,
                                                 event_monitor_id = monitor.monitor_key,
                                                 event_monitor_name = monitor.name,
                                                 event_observer_name = observer.name,
                                                 event_type = 'PERSON')
                            event.save()

                            clients = observer.clients.values()
                            for client in clients:
                                client = models.Client.objects.filter(name = client['name'])[0]
                                if client.active:
                                    channels = client.channels.values()
                                    for channel in channels:
                                        channel = models.Channel.objects.filter(id = channel['id'])[0]
                                        if channel.channel_type == 'telegram':
                                            telegram_notificator.notificate_client(monitor, channel, client, screenshot_file_name)
                                        if channel.channel_type == 'voice':
                                            voice.notificate_client(monitor, channel, client)
                            monitor.last_trigger = now
                            monitor.save()
                        else:
                            if len(persons) == 0:
                                print('No hay personas detectadas en el movimiento')
                                os.remove(origin_path + '/' + screenshot_file_name)
                            if not backend_response:
                                print('No se pudo contactar backend')
                        if backend_response: 
                            break
                        
                        
            else:
                print('No se procesa movimiento porque esta fuera de schedule')
        

        