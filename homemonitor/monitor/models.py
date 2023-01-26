from django.db import models
import json
from datetime import datetime, timedelta


# Create your models here.


class Observer(models.Model):
    name = models.CharField(max_length=12)
    # backend = models.ForeignKey(
    #     'Backend',
    #     on_delete=models.CASCADE,
    #     )
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    # schedule = models.CharField(max_length=200)
    schedule_off = models.BooleanField(help_text='Desactiva schedule de notificaciones. Notificaciones siempre se envian.')
    schedule = models.ManyToManyField('schedule')
    monitors = models.ManyToManyField('monitor')
    backends = models.ManyToManyField('backend')
    clients = models.ManyToManyField('client')

    def set_schedule(self, x):
        self.schedule = json.dumps(x)

    def get_schedule(self):
        return json.loads(self.schedule)

    def __str__(self):
        return self.name   

class Origin(models.Model):
    name = models.CharField(max_length=12)
    api_key = models.CharField(max_length=35)
    group_key = models.CharField(max_length=20)
    origin_ip_address = models.GenericIPAddressField()
    origin_port = models.PositiveIntegerField(default=8000)

    def __str__(self):
        return self.name    

class Monitor(models.Model):
    name = models.CharField(max_length=12)
    monitor_key = models.CharField(max_length=20)
    origin = models.ForeignKey(
        'Origin',
        on_delete=models.CASCADE,
        )
    yesterday = datetime.today() - timedelta(days=1)
    timeout = models.PositiveIntegerField(help_text = 'Timeout entre detecciones de personas. En minutos')
    last_trigger = models.DateTimeField(editable = False, blank=True, default = yesterday)
    def __str__(self):
        return self.name
    
class Backend(models.Model):
    name = models.CharField(max_length=40)
    active = models.BooleanField()
    backend_type = models.CharField(max_length=40)
    resource_group = models.CharField(max_length=40, help_text='Nombre del grupo de recursos donde esta Azure Computer Vision')
    account_name = models.CharField(max_length=40, help_text='Nombre del recurso de Azure Computer Vision')
    account_region = models.CharField(max_length=20)
    account_key = models.CharField(max_length=40)
    # azureKey = models.CharField(max_length=35)
    # url = models.URLField()

    def __str__(self):
        return self.name    

class Config(models.Model):
    config_name = models.CharField(max_length=12)
    origin_path = models.CharField(max_length=100)
    aux_path = models.CharField(max_length=100)
    final_path = models.CharField(max_length=100)

    def __str__(self):
        return self.config_name

class Schedule(models.Model):
    name = models.CharField(max_length=12)
    days =  models.CharField(max_length=200)
    hours = models.CharField(max_length=200)

    def set_days(self, x):
        self.days = json.dumps(x)

    def get_days(self):
        return json.loads(self.days)

    def set_hours(self, x):
        self.hours = json.dumps(x)

    def get_hours(self):
        return json.loads(self.hours)

    def __str__(self):
        return self.name

class Client(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField()
    telegram_chat_id = models.PositiveIntegerField(blank=True)
    channels = models.ManyToManyField('channel')
    phone = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return self.name

class Channel(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField()
    channel_type = models.CharField(max_length=30)
    message = models.CharField(max_length=200)
    telegram_key = models.CharField(max_length=50, blank=True)
    twilio_account_sid = models.CharField(max_length=50, blank=True)
    twilio_auth_token = models.CharField(max_length=50, blank=True)
    twilio_from_number = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    event_datetime = models.DateTimeField()
    event_monitor_id = models.CharField(max_length=20)
    event_monitor_name = models.CharField(max_length=12)
    event_observer_name = models.CharField(max_length=12)
    event_type = models.CharField(max_length=12)


    def __str__(self):
        str_datetime = self.event_datetime.strftime("---%m/%d/%Y, %H:%M:%S")
        name = self.event_type + str_datetime
        return name