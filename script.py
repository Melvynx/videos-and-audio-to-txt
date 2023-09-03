import os
import openai
from moviepy.editor import VideoFileClip

# get all video from video folder
videos = os.listdir('videos')
audios = os.listdir('audios')

# for each video, extract audio  and put the audio in the audio folder with the same name
for video in videos:
    video_name = os.path.splitext(video)[0]

    if video_name + '.mp3' in audios:
        continue

    video_path = f'videos/{video}'
    audio_path = f'audios/{video_name}.mp3'
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

# get the "Missing text file" comparing the audio folder with the output folder
# each video must be transcribed and the result must be put in the output folder with the same name
audio_to_transcribe = os.listdir('audios')
output = os.listdir('output')

# remove audio from audio_to_transcribe if it is already in the output folder
for audio in audio_to_transcribe:
    txt_name = os.path.splitext(audio)[0] + '.txt'
    if txt_name in output:
        audio_to_transcribe.remove(audio)

print(audio_to_transcribe)


# Load your API key from an environment variable or secret management service
openai.api_key = "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"

def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
    return transcription['text']

for audio_file in audio_to_transcribe:
    print("Currently transcribing: ", audio_file)

    result = transcribe_audio(f'audios/{audio_file}')
    txt_name = os.path.splitext(audio_file)[0] + '.txt'

    with open(f'output/{txt_name}', 'w') as txt_file:
        txt_file.write(result)
