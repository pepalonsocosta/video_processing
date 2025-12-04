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
