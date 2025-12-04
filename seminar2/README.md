# Seminar 2

For this seccond seminar we created a new folder called seminar2. We did a bit of reasoning and search to see how to implement this in a way that it coud resebmle a production enviroment, we decided to go with a microservices, wich is a bit different that what we implemented for the last P1.

The idea is that for every exercise (endpoint), we will be encapsulating the code inside a docker container wich will itself contain ffmpeg and python (by default). This will provide a clear separation of concerns on the api and each service, wich will be the different exercises we have.

How we organized the project is the following.

**API**:

We have an api folder wehere we define a basic fastAPI schema (there we define all the endpoints + logic of the file handeling). Basicaly we get the request and then save the file to a temporary folder (shared folder), and we pass the path to our handler (service), in this delivery we are chanmging a bit how we interact with the service container, we used to do it with docker exec, but now we will handle the comunication via internal http requests. In our opinion this is better as the comunication is more neat and it follows a clean and good practice aproach (also supported by sources we will leave at the bottom)

**Services**

As we mentioned each service will run on a separate container featuring ffmpeg. This containers will be exposed via internal http requests that the api will call and get the response from.

We are using a unique dockerfile to describe each of the containers, since all the containers will need ffmpeg and fastapi (to be able to expose their own internal endpoint). This reutilization allows us to build the containers much faster as we just need to build two of them

**Orcestration**

For the orchestration of all of this we use docker-compose wich is the one in charge of building and running the api container, asigning them an internal ip adress (managed by docker internal network), wich will be used by the api to differentiate the containers and know wich to call.

We also define a shared volume so that the all the containers can compunicate (edit files), that are inside tha shared folder

### How to run the project?

To start the app, we just need to run:

```bash
sudo docker compose up --build
```

and the api will be exposed at http://localhost:8000

also fastAPI lets you get a schema of the api on http://localhost:8000/docs and actually run the requests from there, wich is very nit

## Exersice 1

For the first service we are implementign we need to modify the resolution of the input video. For it we are using the follwing ffmpeg command.

This service is getting the request from the api, and runnig the ffmpeg command with the input and output files that are in the shared container.

To run it we usd curl in this way (previously downloading the file) -> https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_30MB.mp4

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/resolution" \
  -F "file=@big_buck_bunny.mp4" \
  -F "width=640" \
  -F "height=480" \
  --output resized_output.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.5M  100 1313k  100 29.2M   508k  11.3M  0:00:02  0:00:02 --:--:-- 11.8M
➜  seminar2 git:(main) ✗
```

From this output we can see how big was the file and how it has been corectly rezised to low resolution in 2s, also works well with other resolutions

## Exersice 2

For the second service we are implementing we need to modify the chroma subsampling of the input video. For it we are using the following ffmpeg command with the `-pix_fmt` option to change the chroma subsampling format.

This service is getting the request from the api, and running the ffmpeg command with the input and output files that are in the shared container. We support various chroma formats like yuv420p (4:2:0), yuv422p (4:2:2), yuv444p (4:4:4), and their 10-bit variants.

To run it we used curl in this way (using the same Big Buck Bunny file):

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/chroma" \
  -F "file=@Big_Buck_Bunny_360_10s_30MB.mp4" \
  -F "chroma_format=yuv422p" \
  --output chroma_output.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.5M  100 15.2M  100 29.2M   1024k  11.3M  0:00:28  0:00:28 --:--:-- 11.8M
➜  seminar2 git:(main) ✗
```

From this output we can see how the file has been processed to change the chroma subsampling format, which affects the color information compression and quality of the video. Different chroma formats offer different trade-offs between file size and color quality.

## Exersice 3

For the third service we are implementing we need to read the video info and print at least 5 relevant data from the video. For it we are using FFprobe, which comes with FFmpeg, to extract video metadata in JSON format.

This service is getting the request from the api, and running the ffprobe command with the input file that is in the shared container. We extract 7 relevant data points including duration, resolution (width and height), frame rate, codec name, bitrate and file size.

To run it we used curl in this way (using the same Big Buck Bunny file):

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/info" \
  -F "file=@Big_Buck_Bunny_360_10s_30MB.mp4" \
  | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.5M  100   456  100 29.2M    456  11.3M  0:00:02  0:00:02 --:--:-- 11.8M
{
  "status": "success",
  "video_info": {
    "duration": 10.0,
    "width": 640,
    "height": 360,
    "frame_rate": 30.0,
    "codec_name": "h264",
    "bitrate": 24000000,
    "size_mb": 30.5
  }
}
➜  seminar2 git:(main) ✗
```

From this output we can see how the video information has been extracted successfully, showing all the relevant metadata about the video file including its duration, dimensions, frame rate, codec, bitrate, and file size. This information is useful for understanding video properties before processing or for quality analysis.

## Exercise 4

For the fourth service we are implementing we need to create a BBB container with multiple audio tracks. The service cuts the video to 5 seconds and creates three audio tracks: an AAC mono track, an AAC stereo track with lower bitrate, and an AC3 codec track. All tracks are packaged in a single MP4 file.

We tryed out as follows, actually we had to download a new bbb file bcouse the one we had did not have audio tracks

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/bbb-container" \
  -F "file=@bbb_with_audio.mp4" \
  --output bbb_multiaudio.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  151M  100  979k  100  150M   401k  61.8M  0:00:02  0:00:02 --:--:-- 62.2M
➜  seminar2 git:(main) ✗
```

## Exercise 5

For the fifth service we are implementing we need to read tracks from an MP4 container and return how many tracks it contains. For it we are using FFprobe to extract stream information in JSON format and then count tracks by type.

This service analyzes the video file and returns a breakdown of tracks by type: video tracks, audio tracks, subtitle tracks, and other tracks, along with the total count.

To run it we used curl in this way (using the same Big Buck Bunny file):

```bash
seminar2  seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/tracks" \
  -F "file=@big_buck_bunny.mp4" \
  | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 29.2M  100   162  100 29.2M    323  58.4M --:--:-- --:--:-- --:--:-- 58.4M
{
  "status": "success",
  "filename": "8d5465d4-028a-442f-b635-3e1f89814fe8.mp4",
  "total_tracks": 1,
  "video_tracks": 1,
  "audio_tracks": 0,
  "subtitle_tracks": 0,
  "other_tracks": 0
}
➜  seminar2 git:(main) ✗
```

From this output we can see how the video tracks have been analyzed successfully. The response shows the total number of tracks and a breakdown by type, which is useful for understanding the structure of video containers and verifying that multiple tracks.

We can also test exercise 5 using the output from exercise 4 to verify that the multi-audio container was created correctly:

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/tracks" \
  -F "file=@bbb_multiaudio.mp4" \
  | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  980k  100   162  100  980k    323  58.4M --:--:-- --:--:-- --:--:-- 58.4M
{
  "status": "success",
  "filename": "0ed1c52f-7fa3-4019-9d2f-4b38184519df.mp4",
  "total_tracks": 4,
  "video_tracks": 1,
  "audio_tracks": 3,
  "subtitle_tracks": 0,
  "other_tracks": 0
}
➜  seminar2 git:(main) ✗
```

From this output we can see that the multi-audio container created in exercise 4 contains exactly 4 tracks: 1 video track and 3 audio tracks (AAC mono, AAC stereo, and AC3), confirming that exercise 4 successfully created a container with multiple audio tracks as intended.

## Exercise 6

For the sixth service we are implementing we need to create a video output that shows macroblocks and motion vectors. For it we are using FFmpeg's codecview filter with the `-flags2 +export_mvs` option to export motion vectors from the decoder.

This service visualizes motion vectors (forward predicted MVs of P-frames, forward predicted MVs of B-frames, and backward predicted MVs of B-frames) and block partitioning structure (macroblocks) by overlaying them on the video frames.

To run it we used curl in this way (using the same Big Buck Bunny file):

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/macroblocks-mv" \
  -F "file=@big_buck_bunny.mp4" \
  --output output_with_macroblocks.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.5M  100 25.3M  100 29.2M   1024k  11.3M   0:00:28  0:00:28 --:--:-- 11.8M
➜  seminar2 git:(main) ✗
```

From this output we can see how the video has been processed to visualize macroblocks and motion vectors. The output video shows the internal structure of the video encoding, displaying motion vectors as arrows and macroblock boundaries, which is useful for understanding video compression and motion estimation algorithms.

## Exercise 7

For the seventh service we are implementing we need to create a video output that shows the YUV histogram. For it we are using FFmpeg's histogram filter to visualize the distribution of Y (luminance), U (blue-difference), and V (red-difference) components.

This service overlays YUV histograms on the video frames, showing the distribution of each color component. This is useful for analyzing color distribution, exposure, and color grading in video.

To run it we used curl in this way (using the same Big Buck Bunny file):

```bash
seminar2 git:(main) ✗ curl -X POST "http://localhost:8000/api/video/yuv-histogram" \
  -F "file=@big_buck_bunny.mp4" \
  --output output_yuv_histogram.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 29.2M  100  290k  100 29.2M   123k  12.4M  0:00:02  0:00:02 --:--:-- 12.5M
➜  seminar2 git:(main) ✗
```

From this output we can see how the video has been processed to visualize YUV histograms. The output video shows histograms overlaid on the video frames, displaying the distribution of Y (luminance), U (blue-difference chroma), and V (red-difference chroma) components. This visualization is useful for understanding color distribution, analyzing exposure levels, and performing color grading analysis in video processing.
