from app.core.jwt import create_access_token, decode_access_token

# Create token
token = create_access_token(user_id=1)

print("Generated token:", token)

# Decode token
payload = decode_access_token(token)

print("Decoded payload:", payload)
print("User ID:", payload["sub"])