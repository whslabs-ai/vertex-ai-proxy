from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
from auth import VertexAITokenManager
import json
from typing import Optional, AsyncGenerator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_id: str
    location: str = "us-central1"
    port: Optional[int] = 8080  # Default port

    class Config:
        env_file = ".env"


app = FastAPI()
settings = Settings()
token_manager = VertexAITokenManager()

VERTEX_AI_BASE_URL = f"https://{settings.location}-aiplatform.googleapis.com/v1beta1/projects/{settings.project_id}/locations/{settings.location}"


async def process_stream(response: httpx.Response) -> AsyncGenerator[bytes, None]:
    """Process streaming response from Vertex AI"""
    async for line in response.aiter_text():
        if line.strip():
            if line.strip() == "data: [DONE]":
                yield "[DONE]".encode("utf-8")
                break
            yield f"{line}\n".encode("utf-8")


async def forward_request(request: Request, endpoint_path: str) -> JSONResponse:
    # Get fresh token
    token = token_manager.get_token()

    # Get request body
    body = await request.json()

    # Check if streaming is requested
    stream = body.get("stream", False)

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream" if stream else "application/json",
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

            if stream:
                return StreamingResponse(
                    process_stream(response), media_type="text/event-stream"
                )
            else:
                # For non-streaming requests, collect the full response
                full_response = ""
                async for chunk in response.aiter_text():
                    full_response += chunk
                return JSONResponse(
                    content=json.loads(full_response), status_code=response.status_code
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
