# test_firestore.py
from firebase.firebase_config import db

# Reference a collection and document
doc_ref = db.collection("analytics").document("pageViews")

# Add sample data
doc_ref.set({
    "page1": 5,
    "page2": 10,
    "page3": 15
})

print("Data added to Firestore successfully!")
