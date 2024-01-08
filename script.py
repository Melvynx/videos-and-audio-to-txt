from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

import os

from moviepy.editor import VideoFileClip
from openai import OpenAI
import shutil


client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
    # Otherwise use: api_key="Your_API_Key",
    api_key=os.environ.get("OPENAI_API_KEY")
)

# get all video from video folder
videos = os.listdir("videos")
audios = os.listdir("audios")

# for each video, extract audio  and put the audio in the audio folder with the same name
for video in videos:
    video_name = os.path.splitext(video)[0]

    if video_name + ".mp3" in audios:
        continue

    video_path = f"videos/{video}"
    audio_path = f"audios/{video_name}.mp3"
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

# get the "Missing text file" comparing the audio folder with the output folder
# each video must be transcribed and the result must be put in the output folder with the same name
audios = os.listdir("audios")
output = os.listdir("output")
audio_to_transcribe = []

# remove audio from audio_to_transcribe if it is already in the output folder
for audio in audios:
    txt_name = os.path.splitext(audio)[0] + ".txt"
    if txt_name not in output:
        audio_to_transcribe.append(audio)


def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    return transcription.text


for audio_file in audio_to_transcribe:
    print("Currently transcribing: ", audio_file)

    result = transcribe_audio(f"audios/{audio_file}")
    txt_name = os.path.splitext(audio_file)[0] + ".txt"

    with open(f"output/{txt_name}", "w") as txt_file:
        txt_file.write(result)

# get the "Missing text file" comparing the output folder with the course folder
# each output must be "formated" and the result must be put in the course folder with the same name
output = os.listdir("output")
output_to_format = []
course = os.listdir("course")

# add to output_to_format if it is not in the course folder
for txt in output:
    if txt not in course:
        output_to_format.append(txt)

print("=== File to format with GPT4.5 ===")
print(output_to_format)

prompt_courses = """Contexte : 
Tu es un professeur de code dont le but est de créer un cours en markdown compréhensible en fonction du texte qui te sera donné.
Tu es pédagogique, intelligent et tu as enseigné dans les écoles les plus prestigieuses du monde.

Objectif : 
Créer un cours aéré en utilisant des titres et des sous-titres qui résument le contenu de la "transcription" qui te sera donnée.

Critères : 
- Séparer les sujets de la transcription en titres et sous-titres.
- Utiliser un titre maximum de "h2".
- Parler à la première personne du pluriel et tutoyer l'élève.
- Utiliser les syntaxes markdown telles que **gras** ou *italique* si nécessaire.
- Expliquer les choses de manière simple.
- Utiliser des doubles retours à la ligne fréquents pour aérer le texte.
- Les titres doivent être simples et concis.
- Ne jamais utiliser de titre "h1".
- Commencer le cours par une introduction claire expliquant les sujets qui seront abordés, point par point.
- N'hésites pas à utiliser du code, des exemples ou autre pour illustrer ce que je dis dans la vidéo.
- TU TUTOIE TOUJOURS L'ÉLÈVE.

Format de réponse : 
- Un texte valide en markdown.
- Ne jamais utiliser de "h1" (#).
- Utiliser des doubles retours à la ligne pour aérer le texte. C'EST IMPORTANT.
- Renvoyer la réponse sans ajouter de "```" avant ou après.""";

prompt_talking = """Context:
Tu es un outil qui résume des discution entre deux individus principalement au sujet d'une formation BeginJavaScript.

Goal:
Tu dois ressortir toutes les informations pertinentes de la discussion.
Tout ce qui est percutant et qui pourrait considérablement améliorer le marketing de ma foramtion.

Criteria:
- Séparer les arguments
- Utiliser des doubles retours à la ligne fréquents pour aérer le texte.

Format de réponse :
Tu peux renvoyer le text en markdown pour que je puisse le mettre sur mon site web.
"""

# for each output to format, use "ChatGPT4 chat completion" with a custom prompt
for txt in output_to_format:
    print("Currently formatting: ", txt)
    with open(f"output/{txt}", "r") as txt_file:
        text = txt_file.read()

    prompt = f"""Q: {text}"""

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": prompt_courses,
            },
            {"role": "user", "content": text},
        ],
    )

    final_result = response.choices[0].message.content

    # save it in the course folder with the same name
    with open(f"course/{txt}", "w") as txt_file:
        txt_file.write(final_result)

# for each text that is in course, your will create a `final` folder with a subfolder named as
# the current file and you will add :
# - video.mp4 if exist (for this file)
# - audio.mp4 if exist
# - transcribe.txt if exist
# - course.md

courses = os.listdir("course")

for course in courses:
    course_name = os.path.splitext(course)[0]
    final_path = f"final/{course_name}"
    if not os.path.exists(final_path):
        os.makedirs(final_path)

    if course_name + ".mp4" in videos:
        video_path = f"videos/{course_name}.mp4"
        shutil.move(video_path, f"{final_path}/video.mp4")

    if course_name + ".mp3" in audios:
        audio_path = f"audios/{course_name}.mp3"
        shutil.move(audio_path, f"{final_path}/audio.mp3")

    if course_name + ".txt" in output:
        txt_path = f"output/{course_name}.txt"
        shutil.move(txt_path, f"{final_path}/transcribe.txt")

    if course_name + ".txt" in course:
        course_path = f"course/{course_name}.txt"
        shutil.move(course_path, f"{final_path}/course.md")
