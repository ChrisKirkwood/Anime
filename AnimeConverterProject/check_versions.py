import google.cloud.speech as speech
import google.cloud.translate_v2 as translate
import google.cloud.texttospeech as texttospeech
import pysrt
import pydub
import moviepy.editor as mp
import vlc

try:
    print("pysrt is installed")
except AttributeError:
    print("pysrt version could not be determined")

try:
    print("pydub version:", pydub.__version__)
except AttributeError:
    print("pydub version could not be determined")

try:
    print("moviepy version:", mp.__version__)
except AttributeError:
    print("moviepy version could not be determined")

# Google Cloud packages might not have __version__ attribute
print("google-cloud-speech installed")
print("google-cloud-translate installed")
print("google-cloud-texttospeech installed")

try:
    print("vlc version:", vlc.__version__)
except AttributeError:
    print("vlc version could not be determined")
