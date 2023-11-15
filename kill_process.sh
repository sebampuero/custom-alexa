kill -9 $(ps aux | grep '[p]ython3 -u /home/pi/talk2pi/start.py' | awk '{print $2}')
