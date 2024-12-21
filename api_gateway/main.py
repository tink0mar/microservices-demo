from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

services = {
    "apartments-api": "http://apartment_api:8000",
    "booking-api": "http://booking_api:8001",
    "search-api": "http://search_api:8002",
}


def forward_request(
    service_url: str, method: str, path: str, body=None, headers=None
):
    if not path.endswith("/"):
        path += "/"  # Append trailing slash if missing
    url = f"{service_url}{path}"
    response = requests.request(method, url, json=body, headers=headers)
    return response


@app.api_route(
    "/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def gateway(service: str, path: str, request: Request):
    if service not in services.keys():
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = services[service]
    body = (
        await request.json()
        if request.method in ["POST", "PUT", "PATCH"]
        else None
    )
    headers = dict(request.headers)

    response = forward_request(
        service_url, request.method, f"/{path}", body, headers
    )

    return JSONResponse(
        status_code=response.status_code,
        content=response.json() if response.content else None,
    )
