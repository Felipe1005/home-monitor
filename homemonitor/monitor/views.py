from django.http import HttpResponse
from . import monitor

# Create your views here.

def motionDetect(request, monitor_key):
    monitor.process_movement(monitor_key)
    return HttpResponse("OK save screenshot for monitor key = " + monitor_key)

