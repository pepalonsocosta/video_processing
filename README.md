# Seminar 1

Hey! for this exercises implemented on python we used uv packet manager -> https://github.com/astral-sh/uv, on the exersises we will leave some insctructions on how to run the code smothly. Of course it can be also runned in any way you like!

## ex-1

For this first exercise we just installed ffmpeg, in this case in linux using apt packet manager
by running it on the terminal we get this result:

![ex1](./s1/exercise1.png)

## ex-2

For this second exeercise we implemented the Seminar1 class with the methods:

- rgb_to_yuv: transforms from RGB space to YUV

- yuv_to_rgb: the inverse transformation

We declared this methods using the @staticmethod decorator to avoid using self notation

For running you can just run the python file (rgb values can be edited on the same file)

using uv that woud be:

```python
uv run first_seminar.py
```

uv will create a virtual environment to run the file on it

## ex-3

For this exercise we investigated diferent ways to rezise/compress an image into a lower quality.

We ended up using the -q:v factor, wich given a compression factor that can range in between

the full command we used is

```bash
ffmpeg -i image_to_resize.jpeg -q:v 31 compressed_image.jpeg
```

For the method we basicaly created a wrapper around this command, where we pass an image file path and a compression_factor

For the two images we chose we got the following results for a compression factor of 31 (the max ffmpeg allows)

![ex2](./s1/image_to_resize.jpg)
![ex2](./s1/compressed_image.jpg)

## ex-4

For this exercise we implemented the `serpentine` method, which reads bytes from a JPEG file and applies the serpentine (zigzag) scanning pattern used in JPEG compression.

The method processes the file in 8x8 blocks (64 bytes each) and applies the zigzag pattern to convert the 2D matrix into a linear sequence. This pattern is used in JPEG compression after DCT and quantization to group high-frequency components together, making them more efficient for run-length encoding.

We created a helper method ( private ) for clarity `_generate_zigzag_indices`

The implementation includes:

- `_generate_zigzag_indices()`: Helper method that generates the zigzag scan pattern for an 8x8 matrix
- `serpentine(jpeg_path)`: Main method that reads the JPEG file and applies the zigzag scanning pattern

When running the script, it processes the image file and outputs the total bytes processed and the number of 8x8 blocks.
