# test_firestore.py
import hashlib
from firebase_config import db

# Admin credentials
email = "dvsteja2@gmail.com"
password = "Saiteja@4329"
hashed_password = hashlib.sha256(password.encode()).hexdigest()

# Reference to the admin collection
admin_ref = db.collection("admin").document(email)

# Add admin data
admin_ref.set({
    "email": email,
    "password": hashed_password,
    "role": "admin"
})

print("Admin user added to Firestore successfully!")
