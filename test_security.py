from app.core.security import hash_password, verify_password

password = "MySecurePassword123"

hashed = hash_password(password)

print("Hashed password:", hashed)
print("Correct password:", verify_password(password, hashed))
print("Wrong password:", verify_password("WrongPassword", hashed))