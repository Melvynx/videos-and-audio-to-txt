import os, ffmpeg


def compress(video_path):
    video_name = os.path.splitext(video_path)[0]
    output_path = f"compressed/{video_name}.mp4"
    ffmpeg.input(video_path).output(output_path, crf=30).run()


path = f"IMG_4474.MOV"

compress(path)
