import glob
from threading import Thread
from feedback_generation import SpeechFeedbackGenerator
from dotenv import load_dotenv

load_dotenv()  # loads environment variables from .env file


# Creates SpeechFeedbackGenerator object and calls summary method
def get_summary(audio):
    sfg = SpeechFeedbackGenerator(audio)
    sfg.summary()


# Get all audio filenames in audio_files folder
audio_files = glob.glob("./audio_files/*")

# Concurrently calls get_summary() method for each audio
for audio in audio_files:
    thread = Thread(target=get_summary, args=(audio,))
    thread.start()
