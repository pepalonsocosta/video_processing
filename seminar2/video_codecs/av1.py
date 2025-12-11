import subprocess

class AV1:

    @staticmethod
    def encode(video_path, output_path):
        cmd = ["ffmpeg", "-y", "-i", video_path, "-c:v", "libaom-av1", "-crf", "50", "-cpu-used", "6", "-b:v", "0", "-c:a", "copy", output_path]
        subprocess.run(cmd, check=True)