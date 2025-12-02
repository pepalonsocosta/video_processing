from fastapi import FastAPI

app = FastAPI(
    title="Practice1 API",
    description="P1 - API and Dockerization",
    version="0.1.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

