import bcrypt

password = "SecretPassword55"
password_new = str.encode(password)
hashed = bcrypt.hashpw(password_new, bcrypt.gensalt())

if bcrypt.checkpw(password_new, hashed):
    print("True")
else:
    print("ff")