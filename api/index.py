from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"] # important
)
# Global middleware for CORS headers
# @app.middleware("http")
# async def add_cors_headers(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "*"
#     return response

# @app.options("/{full_path:path}")
# async def options_handler(full_path: str):
#     """Catch all OPTIONS requests with CORS headers"""
#     response = JSONResponse(content={})
#     response.headers["Access-Control-Allow-Origin"] = "*"

# Enable CORS for POST requests from any origin
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# @app.options("/api/latency")
# async def options_latency():
#     response = JSONResponse(content={})
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "*"
#     return response

# Load telemetry JSON once
with open(os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")) as f:
    telemetry = json.load(f)

# Health check endpoint
# @app.get("/")
# def root():
#     return {"message": "Hello FastAPI on Vercel!"}

# Main latency endpoint
@app.post("/api/latency")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    results = {}
    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies),
        }

    response = JSONResponse(content=results)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
