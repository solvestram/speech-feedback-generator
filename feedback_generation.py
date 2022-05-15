import speech_recognition as sr
from nltk import FreqDist
from nltk.corpus import stopwords
import audioread


class SpeechFeedbackGenerator:
    """
    Accepts path to audio in constructor and creates feedback for that audio

    Attributes
        path_to_audio: Path to audio file
        audio_data: Contains audio channels count, sample rate and duration
        text_from_speech: Text converted from speech
        word_list: Text converted to list with split()
        filtered_word_list: word_list without stop words
        filler_words: List of filler words
        profane_words: List of potentially offensive words
        slang_words: List of slang words
    """

    def __init__(self, path_to_audio):
        # Save path to audio
        self.path_to_audio: str = path_to_audio

        # Get audio data with audioread
        with audioread.audio_open(path_to_audio) as audio:
            self.audio_data: dict = {
                'channels': audio.channels,
                'sample_rate': audio.samplerate,
                'duration': audio.duration,
            }

        # Converting speech to text
        r = sr.IbmSpeechRecognizer()

        # Get speech transcript
        print("Trying to recognize the speech...")
        self.text_from_speech: str = r.recognize(path_to_audio)  # Converted text
        print("Recognition completed.")

        # Converting to list
        self.word_list: list = self.text_from_speech.split()

        # Creating filtered list without stopwords
        stop_words: set = set(stopwords.words('english'))
        self.filtered_word_list: list = [word for word in self.word_list if not word.lower() in stop_words]

        # Filler words list
        # Source (modified): https://github.com/words/fillers/blob/main/data.txt
        with open("data_files/filler_words.txt", "r") as f:
            self.filler_words: list = f.read().split("\n")

        # Profane words list
        # Source: https://www.cs.cmu.edu/~biglou/resources/
        with open("data_files/profane_words.txt", "r") as f:
            self.profane_words: list = f.read().split("\n")

        # Slang words list
        # Scraped from: https://www.urbandictionary.com (modified)
        with open("data_files/slang_words.txt", "r") as f:
            self.slang_words: list = f.read().split("\n")

    def check_speech_speed(self) -> float:
        """ Calculates speech speed. """

        words_per_minute = len(self.word_list) / self.audio_data['duration'] * 60

        return words_per_minute

    def check_word_repetition(self) -> dict:
        """ Count word repetitions for each words. The words that are repeated only once are filtered. """

        fdist = FreqDist()
        for word in self.filtered_word_list:
            if word == '%HESITATION':
                fdist['%HESITATION'] += 1
                continue

            fdist[word.lower()] += 1

        repeated_words = {word: count for word, count in dict(fdist).items() if count > 1}

        return repeated_words

    def check_filler_words(self) -> list:
        """ Detected filler words in speech. """

        found_filler_words = []
        for word in self.word_list:
            if word.lower() in self.filler_words or word == '%HESITATION':
                found_filler_words.append(word)

        return found_filler_words

    def check_profanity(self) -> list:
        """ Detects profane words in speech """

        found_profane_words = []
        for word in self.word_list:
            if word.lower() in self.profane_words:
                found_profane_words.append(word)

        return found_profane_words

    def check_slang_words(self) -> list:
        """ Detects slang words in speech """

        found_slang_words = []
        for word in self.word_list:
            if word.lower() in self.slang_words:
                found_slang_words.append(word)

        return found_slang_words

    def generate_feedback(self) -> dict:
        """ Generates feedback for speech in a dictionary form """

        feedback = dict()

        # feedback on speed
        speech_speed = self.check_speech_speed()
        if speech_speed > 160:
            feedback['speech_speed'] = "Your speech speed is faster than recommended rate. You may consider speaking more slowly."
        elif speech_speed < 140:
            feedback['speech_speed'] = "Your speech speed is slower than recommended rate. You may consider speaking faster."
        else:
            feedback['speech_speed'] = "Your speech speed is within recommended range."

        # feedback on filler words
        total_word_count = len(self.word_list)
        filler_word_count = len((self.check_filler_words()))

        filler_word_percentage = filler_word_count / total_word_count * 100

        if filler_word_percentage > 1.28:
            feedback['filler_words'] = "The number of filler words is higher than recommended. This may make speech seem less credible."
        else:
            feedback['filler_words'] = "The number of filler words is within recommended range."

        # feedback on profane words
        profane_word_count = len(self.check_profanity())

        if profane_word_count == 0:
            feedback['profane_words'] = "No profane words found."
        else:
            feedback['profane_words'] = "Some potentially profane words found. It might be better to avoid them unless necessary."

        # feedback on slang words
        slang_word_count = len(self.check_slang_words())

        if slang_word_count == 0:
            feedback['slang_words'] = "No slang words found."
        else:
            feedback['slang_words'] = "Some potentially slang words found. It might be better to avoid them unless necessary."

        # feedback on word repetition
        repeated_words_count = len(self.check_word_repetition())

        if repeated_words_count == 0:
            feedback['word_repetition'] = "No word repetition found."
        else:
            feedback['word_repetition'] = "There are some word repetitions in your speech. You may have a look at how many times each word is repeated and consider reducing the number of repetitions."

        return feedback

    def summary(self):
        """ Creates the summary for the speech. It includes extracted speech features data and feedback. """

        feedback = self.generate_feedback()

        print("----------------------------------------")
        print("SUMMARY FOR AUDIO:", self.path_to_audio)
        print("Text from speech:", self.text_from_speech)
        print("Word count:", len(self.word_list))
        print("---")
        print("Speech speed (words per minute):", self.check_speech_speed())
        print("Feedback on speech speed:", feedback['speech_speed'])
        print("---")
        print("Filler words count:", len(self.check_filler_words()), tuple(self.check_filler_words()))
        print("Feedback on filler words:", feedback['filler_words'])
        print("---")
        print("Potentially profane words count:", len(self.check_profanity()), tuple(self.check_profanity()))
        print("Feedback on profanity:", feedback['profane_words'])
        print("---")
        print("Slang words count:", len(self.check_slang_words()), tuple(self.check_slang_words()))
        print("Feedback on slang words:", feedback['slang_words'])
        print("---")
        print("Word repetition:", self.check_word_repetition())
        print("Feedback on word repetition:", feedback['word_repetition'])
        print("----------------------------------------")