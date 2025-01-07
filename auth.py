import google.auth
import google.auth.transport.requests
from datetime import datetime, timedelta


class VertexAITokenManager:
    def __init__(self):
        self.credentials, self.project = google.auth.default()
        self.token = None
        self.token_expiry = None

    def get_token(self):
        # Check if token is expired or about to expire in next 5 minutes
        if (
            not self.token_expiry
            or datetime.utcnow() + timedelta(minutes=5) >= self.token_expiry
        ):
            self._refresh_token()
        return self.token

    def _refresh_token(self):
        auth_req = google.auth.transport.requests.Request()
        self.credentials.refresh(auth_req)
        self.token = self.credentials.token
        # Set token_expiry using the expiry attribute from credentials
        self.token_expiry = self.credentials.expiry
