# Hey! This is our report for 02 - P1. Here we will explain the aproach we though it was better for each exercise and how we implemented.

### Framework

As in S1 we are using uv python manager to handle in a nicer way the dependencies.

For the http api we chose to go with fastapi as it was the one that provided the cleaner and shorter way to define endpoints etc

## Ex 1

For this exercise we created a scaffold for what will be our api contaier wich will serve our program and expose some of the methods we implemented on S1.
As we said we went with fastapi wich allows us to define endpoints like this:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
```

We used uv also for the this container as well, we just created an enpoint for the health to see if our app is working.

We can run the app in dev mode running:

```bash
uv run fastapi dev main.py
```

Then we created a dockerfile to contarize the application, sinde the docker file we just copy the necesary files and run the fastapi framework with uv

We did it like this:

```bash
sudo docker build -t practice1-api .
sudo docker run -p 8000:8000 practice1-api
```
