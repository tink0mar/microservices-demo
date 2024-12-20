from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

services = {
    "/apartments-api": "http://localhost:8000",
    "/booking-api": "http://localhost:8001",
    "/search-api": "http://localhost:8002"
}

async def forward_request(service_url: str, method: str, path: str, body=None, headers=None):
    async with httpx.AsyncClient(proxies=None) as client:
        url = f"{service_url}{path}"
        response = await client.request(method, url, json=body, headers=headers)
        return response

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):
    if service not in services:
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = services[service]
    body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else None
    headers = dict(request.headers)

    response = await forward_request(service_url, request.method, f"/{path}", body, headers)

    return JSONResponse(status_code=response.status_code, content=response.json())
