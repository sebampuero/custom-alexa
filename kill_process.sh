kill -9 $(ps aux | grep '[p]ython3 -u /home/pi/talk2pi/talk2pi.py' | awk '{print $2}')
