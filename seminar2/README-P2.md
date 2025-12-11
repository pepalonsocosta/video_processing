For the P2 we have decides to continue working on the framework we created for S2, since we think it can scale well for this next set of exercises. Just for reference, how the services work on our framework is the following:

- We have an api container running FASTapi py framework, this containers comunicate with our services via http
- Each services is independent and issolated on its own environment , also each ccontainer runs ffmpeg on the backgorund and also servces a small very basic endpoint that is used for internal copmunication with the api (this call only happens inside the local docker compose network).

## Ex 1

Starting with the first exercise we sis some research and found some sources about how to encode a video on this different sources. Those are the most relevant:

- https://trac.ffmpeg.org/wiki/Encode/AV1
- https://trac.ffmpeg.org/wiki/Encode/H.265
- https://trac.ffmpeg.org/wiki/Encode/VP8
- https://trac.ffmpeg.org/wiki/Encode/VP9

Since the encoders were pretty slow and we were constantly hitting timouts and large computing times, we reserched for some optimization for aiming for shorter times, of course trading off quality and larges sizes for the outputs.

We also had to set the flag `-c:a copy` bc we were running into some errors

To ensure a fair comparison of encoding time and file size, we decided to use CRF (Constant Rate Factor) values to maintain similar quality across all codecs. This allows us to compare:

- Encoding time (which codec is faster)
- File size efficiency (which codec achieves better compression at the same quality level)

The CRF values were chosen to optimize for encoding speed while maintaining reasonable quality. We use CRF 50 for AV1, VP8, and VP9 (with cpu-used 6 for faster encoding), and CRF 35 for H265.

The commands we end up using are:

```bash
# av1
ffmpeg -y -i <input_video> -c:v libaom-av1 -crf 50 -cpu-used 6 -b:v 0 -c:a copy <output_video>

# h265
ffmpeg -y -i <input_video> -c:v libx265 -crf 35 -preset medium -c:a copy <output_video>

# vp8
ffmpeg -y -i <input_video> -c:v libvpx -crf 50 -b:v 0 -deadline good -cpu-used 6 -c:a copy <output_video>

# vp9
ffmpeg -y -i <input_video> -c:v libvpx-vp9 -crf 50 -b:v 0 -deadline good -cpu-used 6 -c:a copy <output_video>

```

The implementation we used wass to create a service that woud handle diferent convertions in a docker container. The type of codec to use is passed as a path parameter as

/api/video/convert/{codec}

with options: av1, h265, vp8 and vp9

We tried the api and got this results

```bash
 seminar2 git:(04-p2-transcoding-and-final-work) ✗ curl -X POST "http://localhost:8000/api/video/convert/av1" \
  -F "file=@big_buck_bunny.mp4" \
  --output converted_av1.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.0M  100  807k  100 29.2M  25704   932k  0:00:32  0:00:32 --:--:--  205k
➜  seminar2 git:(04-p2-transcoding-and-final-work) ✗ curl -X POST "http://localhost:8000/api/video/convert/h265" \
  -F "file=@big_buck_bunny.mp4" \
  --output converted_h265.mp4
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.2M  100  973k  100 29.2M  60320  1814k  0:00:16  0:00:16 --:--:--  225k
➜  seminar2 git:(04-p2-transcoding-and-final-work) ✗ curl -X POST "http://localhost:8000/api/video/convert/vp8" \
  -F "file=@big_buck_bunny.mp4" \
  --output converted_vp8.webm
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.5M  100 1301k  100 29.2M   168k  3879k  0:00:07  0:00:07 --:--:--  287k
➜  seminar2 git:(04-p2-transcoding-and-final-work) ✗ curl -X POST "http://localhost:8000/api/video/convert/vp9" \
  -F "file=@big_buck_bunny.mp4" \
  --output converted_vp9.webm
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 30.3M  100 1051k  100 29.2M  63399  1765k  0:00:16  0:00:16 --:--:--  278k
➜  seminar2 git:(04-p2-transcoding-and-final-work) ✗
```

As can be seen above the times and output size for each file were:

- AV1 | 0:32 (32 seconds) | 807 KB
- H265 | 0:16 (16 seconds) | 973 KB
- VP8 | 0:07 (7 seconds) | 1301 KB
- VP9 | 0:16 (16 seconds) | 1051 KB

## Ex 2

For the second exercise we implemented an encoding ladder feature that allows generating multiple versions of the same video at different resolutions. This is useful for adaptive streaming scenarios where different quality levels are needed based on network conditions or device capabilities.

The implementation reuses the existing codec classes from Ex 1, extending them to accept optional width and height parameters for resolution scaling. We use FFmpeg's `-vf scale=WIDTH:HEIGHT` filter to resize the video while maintaining the same codec settings (CRF values) as in Ex 1.

The encoding ladder service creates multiple encodings of the input video at specified resolutions. Supported resolutions are 480p (854x480), 720p (1280x720), and 1080p (1920x1080). The service internally calls the existing encode methods from the codec classes, passing the resolution parameters to generate the ladder.

The implementation we used was to create a new service that handles encoding ladders in a docker container. The endpoint accepts the codec type, video file, and a comma-separated list of resolutions as form parameters:

/api/video/encoding-ladder

with codec options: av1, h265, vp8 and vp9, and resolution options: 480p, 720p, 1080p

We tried the api and got this results

```bash
➜  seminar2 git:(04-p2-transcoding-and-final-work) ✗ curl -X POST "http://localhost:8000/api/video/encoding-ladder" \
  -F "file=@big_buck_bunny.mp4" \
  -F "codec=vp8" \
  -F "resolutions=480p,720p"
{
  "status": "success",
  "codec": "vp8",
  "ladder": [
    {
      "resolution": "480p",
      "width": 854,
      "height": 480,
      "output_path": "ladder_vp8_480p_70b1d853-4654-454d-aa4b-1efcdfe7bef3.webm",
      "file_size_mb": 0.33
    },
    {
      "resolution": "720p",
      "width": 1280,
      "height": 720,
      "output_path": "ladder_vp8_720p_70b1d853-4654-454d-aa4b-1efcdfe7bef3.webm",
      "file_size_mb": 0.51
    }
  ]
}
```

As can be seen above, the encoding ladder successfully generated multiple versions of the video at different resolutions. The response includes metadata for each generated file including resolution, dimensions, output path, and file size. This allows clients to select the appropriate quality level based on their needs.

## Ex 3

For the third exercise we created a web interface using Vite and React to provide a user-friendly GUI for our video processing API. The frontend allows users to upload videos, select codecs, and choose between single conversion or encoding ladder modes.

We implemented calls to both API endpoints (`/api/video/convert/{codec}` and `/api/video/encoding-ladder`) that receive data from user selections in the web interface. The frontend sends the selected video file, codec choice, and resolution preferences to the backend, which processes the requests and returns the converted files or ladder metadata.

To enable communication between the frontend (running on `http://localhost:5173`) and the backend API, we had to enable CORS (Cross-Origin Resource Sharing) in the FastAPI application. This allows the browser to make requests from the frontend origin to the API server.

The web interface provides a simple form where users can:

- Upload a video file
- Select a codec (H265, AV1, VP8, VP9)
- Choose between "Convert" mode (single file output) or "Encoding Ladder" mode (multiple resolutions)
- Select resolutions for the encoding ladder (480p, 720p, 1080p)
- Download the converted file(s) automatically after processing

The implementation uses React hooks for state management and the Fetch API to communicate with the backend endpoints.

To start the frontend, navigate to the frontend directory and run:

```bash
npm i
npm start
```

The application will be available at `http://localhost:5173`.

# Ex 4

For the 4th exercise we used the follwing prompt

`look at the last 3 commits that were done on this branch and from that changes using the git command line.

Try to improve and reduce lines of your code and add unit tests

For the forntent part adapt the styles so it looks like fcb club fanboy page

Make all the changes on this iteration
`

AI change lots of files and most of the improvements he did focused on refactoring code that was repeated.
