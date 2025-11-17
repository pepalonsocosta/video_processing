import subprocess

class Converter:

    @staticmethod
    def rgb_to_yuv(r, g, b):
        
        y = 0.257 * r + 0.504 * g + 0.098 * b + 16
        u = -0.148 * r - 0.291 * g + 0.439 * b + 128
        v = 0.439 * r - 0.368 * g - 0.071 * b + 128
        return y, u, v

    @staticmethod
    def yuv_to_rgb(y, u, v):

        y_prime = y - 16
        u_prime = u - 128
        v_prime = v - 128
        
        r = 1.164 * y_prime + 1.596 * v_prime
        g = 1.164 * y_prime - 0.813 * v_prime - 0.391 * u_prime
        b = 1.164 * y_prime + 2.018 * u_prime

        r = int(round(r))
        g = int(round(g))
        b = int(round(b))

        return r, g, b

    @staticmethod
    def resize_image(image_path, width, height):

        output_path = 'resized_image.jpeg'

        cmd = ['ffmpeg', '-i', str(image_path), '-vf', f'scale={width}:{height}', str(output_path)]
        subprocess.run(cmd, check=True)
        return

r, g, b = 120, 200, 80
y, u, v = Converter.rgb_to_yuv(r, g, b)
print("YUV:", y, u, v)

r2, g2, b2 = Converter.yuv_to_rgb(y, u, v)
print("RGB:", r2, g2, b2)

output_image = Converter.resize_image('./image_to_resize.jpeg', 320, 240)