import pyttsx3
import speech_recognition as sr
import time
from config import VOICE_INDEX, VOICE_SPEED

def speak(text):
    if not text: return
    print(f"Friend: {text}")
    try:
        temp_engine = pyttsx3.init('sapi5')
        voices = temp_engine.getProperty('voices')
        if len(voices) > VOICE_INDEX:
            temp_engine.setProperty('voice', voices[VOICE_INDEX].id)
        temp_engine.setProperty('rate', VOICE_SPEED)
        temp_engine.say(text)
        temp_engine.runAndWait()
        temp_engine.stop()
    except Exception as e:
        print(f"Voice Error: {e}")

def listen(prompt_text="Waiting..."):
    r = sr.Recognizer()
    r.pause_threshold = 0.7
    with sr.Microphone() as source:
        print(f"\r[{prompt_text}]", end="")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            query = r.recognize_google(audio, language='en-in')
            print(f"\rYou: {query}")
            return query.lower()
        except:
            return ""