from werkzeug.security import generate_password_hash, check_password_hash

nuevo_hash = generate_password_hash("Suerte09")
print("Hash generado:", nuevo_hash)

print("Verificación:", check_password_hash(nuevo_hash, "Suerte09"))
