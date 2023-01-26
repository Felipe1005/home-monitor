from django.contrib import admin

# Register your models here.

from .models import Observer, Origin, Monitor, Config, Schedule, Backend, Client, Channel, Event

admin.site.register([Observer, Origin, Monitor, Config, Schedule, Backend, Client, Channel, Event])

class EventAdmin(admin.ModelAdmin):
    fields = ('url', 'title', 'content')
    readonly_fields = ('event_datetime',
                       'event_type',
                       'event_monitor_id',
                       'event_monitor_id',
                       'event_monitor_name',
                       'event_observer_name'
                       )



    