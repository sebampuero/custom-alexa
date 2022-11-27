from gtts import gTTS
from subprocess import call

def say_text(my_text):
    tts = gTTS(my_text, lang='es')
    tts.save('say.mp3')
    call(["mpg123", "say.mp3"]) #apt-get install mpg123

