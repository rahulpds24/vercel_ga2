from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api")
def read_root():
    return {"message": "Welcome to the FASTAPI application! "}