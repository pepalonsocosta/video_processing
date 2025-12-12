import subprocess

class VP8:
    @staticmethod
    def encode(video_path, output_path, width=None, height=None):
        cmd = ["ffmpeg", "-y", "-i", video_path]
        if width and height:
            cmd.extend(["-vf", f"scale={width}:{height}"])
        cmd.extend(["-c:v", "libvpx", "-crf", "50", "-b:v", "0", "-deadline", "good", "-cpu-used", "6", "-c:a", "copy", output_path])
        subprocess.run(cmd, check=True)