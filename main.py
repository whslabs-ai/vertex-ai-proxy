from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from auth import VertexAITokenManager
import json
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_id: str
    location: str = "us-central1"
    port: Optional[int] = 8000  # Default port

    class Config:
        env_file = ".env"


app = FastAPI()
settings = Settings()
token_manager = VertexAITokenManager()

VERTEX_AI_BASE_URL = f"https://{settings.location}-aiplatform.googleapis.com/v1beta1/projects/{settings.project_id}/locations/{settings.location}"


async def forward_request(request: Request, endpoint_path: str) -> JSONResponse:
    # Get fresh token
    token = token_manager.get_token()

    # Get request body
    body = await request.json()

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Construct target URL
    target_url = f"{VERTEX_AI_BASE_URL}/{endpoint_path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=body,
                timeout=60.0,
            )
            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=str(exc))


@app.post("/chat/completions")
async def chat_completions(request: Request):
    return await forward_request(request, "endpoints/openapi/chat/completions")


@app.post("/completions")
async def completions(request: Request):
    return await forward_request(request, "endpoints/openapi/completions")


@app.post("/embeddings")
async def embeddings(request: Request):
    return await forward_request(request, "endpoints/openapi/embeddings")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)  # Use the configurable port
