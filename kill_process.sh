kill -9 $(ps aux | grep '[p]ython3 -u /home/pi/voice_control/talk2pi/talk2pi/talk2pi.py /home/pi/voice_control/talk2pi/talk2pi/alexa.umdl' | awk '{print $2}')
