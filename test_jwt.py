from app.core.security import (
    create_access_token,
    decode_access_token,
)

token = create_access_token({"sub": "1"})

print("Generated token:", token)

payload = decode_access_token(token)

print("Decoded payload:", payload)

invalid_payload = decode_access_token("invalid.token.value")

print("Invalid token:", invalid_payload)
