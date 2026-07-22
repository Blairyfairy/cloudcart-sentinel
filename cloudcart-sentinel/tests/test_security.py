from app.core.config import Settings
from app.core.security import create_access_token, decode_access_token

def test_token_round_trip():
    settings = Settings(jwt_secret="x" * 32, admin_password="password1")
    token = create_access_token("admin", settings)
    assert decode_access_token(token, settings) == "admin"
