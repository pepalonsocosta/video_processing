import subprocess

class H265:

    @staticmethod
    def encode(video_path, output_path, width=None, height=None):
        cmd = ["ffmpeg", "-y", "-i", video_path]
        if width and height:
            cmd.extend(["-vf", f"scale={width}:{height}"])
        cmd.extend(["-c:v", "libx265", "-crf", "35", "-preset", "medium", "-c:a", "copy", output_path])
        subprocess.run(cmd, check=True)