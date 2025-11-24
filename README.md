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
