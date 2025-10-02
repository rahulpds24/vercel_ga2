from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse
import numpy as np
import os
import json


app = FastAPI()

with open(os.path.join(os.path.dirname(__file__),"q-vercel-latency.json")) as f:
    telemetry = json.load(f)


@app.get("/")
def read_root():
    return {"message": "Welcome to the root endpoint!"}

@app.get("/api/latency")
async def get_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 175)

    results = {}
    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptime = [r["uptime"] for r in records]

        results[region] = {
            "avg_latency" : float(np.mean(latencies)),
            "p95_latency" : float(np.percentile(latencies, 95)),
            "avg_uptime" : float(np.mean(uptime)),
            "breaches" : sum(l > threshold for l in latencies),
        }