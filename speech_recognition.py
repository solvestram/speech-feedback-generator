import os
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class IbmSpeechRecognizer:
    def __init__(self):
        # Authentication
        authenticator = IAMAuthenticator(os.environ['IBM_STT_API_KEY'])

        # Create IBM STT object
        self._speech_to_text = SpeechToTextV1(
            authenticator=authenticator
        )

        # Set service url
        self._speech_to_text.set_service_url(
            'https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/639cbc04-9ef1-44cc-b605-1d920852fd51')

        # Set default headers
        self._speech_to_text.set_default_headers(
            {
                'x-watson-learning-opt-out': "true"  # opt out from IBM's data collection
            }
        )

    def recognize(self, file_path: str) -> str:
        """ Makes request to speech to text API and returns transcribed text """

        # Get audio transcript
        with open(file_path, "rb") as audio:
            # get STT results
            result = self._speech_to_text.recognize(
                audio=audio
            ).get_result()

        # Get transcript from result
        transcription = []
        for utterance in result["results"]:
            for hypothesis in utterance["alternatives"]:
                if "transcript" in hypothesis:
                    transcription.append(hypothesis["transcript"])

        return "".join(transcription)
