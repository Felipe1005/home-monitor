from django.urls import path

from . import views

urlpatterns = [
    path('motionDetect/<monitor_key>', views.motionDetect, name='motionDetect'),
]