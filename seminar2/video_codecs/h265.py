import subprocess

class H265:

    @staticmethod
    def encode(video_path, output_path):
        cmd = ["ffmpeg", "-y", "-i", video_path, "-c:v", "libx265", "-crf", "35", "-preset", "medium", "-c:a", "copy", output_path]
        subprocess.run(cmd, check=True)