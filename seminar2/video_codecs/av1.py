import subprocess

class AV1:

    @staticmethod
    def encode(video_path, output_path, width=None, height=None):
        cmd = ["ffmpeg", "-y", "-i", video_path]
        if width and height:
            cmd.extend(["-vf", f"scale={width}:{height}"])
        cmd.extend(["-c:v", "libaom-av1", "-crf", "50", "-cpu-used", "6", "-b:v", "0", "-c:a", "copy", output_path])
        subprocess.run(cmd, check=True)