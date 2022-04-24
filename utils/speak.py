from gtts import gTTS
import pygame
from io import BytesIO

def say_text(my_text):
    tts = gTTS(text=my_text, lang='es')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    pygame.mixer.init()
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)