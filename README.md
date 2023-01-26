# Home Monitor
I have always liked the idea of having my house with video surveillance. However, the true value is that someone (or something) is constantly watching the cameras and notifies me of any news. Cameras by themselves are useless. During a vacation we are not going to be checking our cameras, even if we check them, that something happened right at that moment is unlikely.

There are already many solutions that detect events and make notifications:
* The camera app itself
* NVR with this feature
* MotionEye
* Shinobi

However, I found aspects that I did not like about those solutions. Regarding the camera applications, the problem is that there are many applications and it depends on the camera you have. If you have many cameras of different brands it is very likely that you will require many different applications to see the cameras and configure each of them to notify you based on what they have available. I want something more centralized and agnostic to the model and brand of the camera, I only require that it be compatible with RSTP.

I centralized the cameras using Shinobi NVR (excellent app otherwise). Shinobi supports object detector plugins and also email and telegram notifications. The problem is that the object detection models are extremely computationally expensive so you need to outsource that in case the server is not that powerful and doesn't have a GPU (in my case Shinobi runs on a RaspberryPI).

With my Home Monitor app (I'm not very clever with names) created with Django, Shinobi only consumes it as a webhook when its built-in motion detector is triggered (the motion detector consumes much less computing resources than the object detector). Then with that trigger, Home Monitor consults cloud vision artificial intelligence services (at the moment only using Azure cognitive services, but many cloud providers have similar services) and in case of finding the desired object (ehh, a person) Home Monitor generates the sending of notifications through Telegram and Twilio (phone call with programmed voice).

In addition, Home Monitor has active monitoring hours and days (I don't want to be notified when I'm at home and the person found on video is me), multi-user each with the preferred way to be notified.

![home-monitor-diagram](https://github.com/Felipe1005/home-monitor/raw/main/home-monitor.png)

The system is as follows. Shinobi via RTSP is connected to the cameras and has the motion detector configured. When the Shinobi motion detector is activated via webhook, it consumes Home Monitor indicating that the camera had movement. Home Monitor obtains the image of that camera using the Shinobi JPEG api and with that image it consults the vision cloud service to detect objects from Azure through API. In case of detecting people, the users configured by their respective channels are notified. At the moment there is Telegram (using python-telegram-bot) and Twilio (using Twilio python package).
