# Background
* Vertex ai provides openai api
* Vertex ai need to refresh token once expire
* Sample code to refresh token and pass to openai sdk
```python
# Programmatically get an access token
creds, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
# Note: the credential lives for 1 hour by default (https://cloud.google.com/docs/authentication/token-types#at-lifetime); after expiration, it must be refreshed.

# Pass the Vertex endpoint and authentication to the OpenAI SDK
PROJECT_ID = 'PROJECT_ID

'
LOCATION = 'LOCATION

'

##############################
# Choose one of the following:
##############################

# If you are calling a Gemini model, set the MODEL_ID variable and set
# your client's base URL to use openapi.
MODEL_ID = 'MODEL_ID

'
client = openai.OpenAI(
    base_url = f'https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/openapi',
    api_key = creds.token)

# If you are calling a self-deployed model from Model Garden, set the
# ENDPOINT_ID variable and set your client's base URL to use your endpoint.
MODEL_ID = 'MODEL_ID

'
client = openai.OpenAI(
    base_url = f'https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT}',
    api_key = creds.token) 
```
# Task
* Write a simple proxy with fastapi and uvicorn to refresh token and forward request to google vertex ai openai api DO NOT USE openai sdk
* Make refresh token into a class
* User send openai compatible request to the proxy, and the proxy will refresh token and forward request to google api
* Support all openai api standards
* Can change model in request body