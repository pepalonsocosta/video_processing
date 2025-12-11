import subprocess

class VP8:
    @staticmethod
    def encode(video_path, output_path):
        cmd = ["ffmpeg", "-y", "-i", video_path, "-c:v", "libvpx", "-crf", "50", "-b:v", "0", "-deadline", "good", "-cpu-used", "6", "-c:a", "copy", output_path]
        subprocess.run(cmd, check=True)