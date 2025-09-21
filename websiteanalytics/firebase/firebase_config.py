import firebase_admin
from firebase_admin import credentials, firestore

# Replace this path with the actual path to your JSON file
cred = credentials.Certificate("websiteanalytics/firebase/serviceAccountKey.json")

# Initialize Firebase app
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
