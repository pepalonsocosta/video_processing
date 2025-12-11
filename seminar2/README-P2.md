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
