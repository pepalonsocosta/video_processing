import subprocess
import os

def run_ffmpeg_in_container(ffmpeg_args, container_name="practice1-ffmpeg-1"):

    cmd = ['docker', 'exec', container_name, 'ffmpeg'] + ffmpeg_args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

