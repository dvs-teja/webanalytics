# 📊 Website Analytics Dashboard - Setup Guide

A real-time website analytics application built with Reflex (Python) and Firebase.

## 🛠️ Project Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Firebase account

### 1. Clone the Repository
```bash
git clone https://github.com/dvs-teja/webanalytics.git
cd webanalytics
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install reflex firebase-admin
```

### 4. Firebase Setup

#### 4.1 Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name
4. Click "Create project"

#### 4.2 Setup Firestore Database
1. Go to **Firestore Database**
2. Click "Create database"
3. Choose "Start in test mode"
4. Select a location
5. Click "Done"

#### 4.3 Generate Service Account Key
1. Go to **Settings** > **Project settings**
2. Click **Service accounts** tab
3. Click "Generate new private key"
4. Download the JSON file
5. Rename to `serviceAccountKey.json`
6. Place in: `websiteanalytics/firebase/serviceAccountKey.json`

### 5. Setup Admin Account

#### Method 1: Using Setup Script (Recommended)

Create `setup_admin.py` in the `websiteanalytics/firebase/` folder:

```python
# setup_admin.py
import hashlib
from firebase_config import db

def setup_admin():
    # Get admin credentials from user input
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Add to Firestore
    admin_ref = db.collection("admin").document(email)
    admin_ref.set({
        "email": email,
        "password": hashed_password,
        "role": "admin"
    })
    
    print(f"Admin user '{email}' added to Firestore successfully!")
    print(f"Hashed password: {hashed_password}")

if __name__ == "__main__":
    setup_admin()
```

**Run the setup script:**
```bash
cd websiteanalytics/firebase
python setup_admin.py
```

#### Method 2: Manual Setup
1. Go to Firestore Console
2. Create collection called `admin`
3. Add document with your email as document ID
4. Add fields:
   - `email`: your-email@example.com
   - `password`: [SHA-256 hash of your password]
   - `role`: admin

**Generate password hash manually:**
```python
import hashlib
password = input("Enter your password: ")
hashed = hashlib.sha256(password.encode()).hexdigest()
print(f"Hashed password: {hashed}")
```

### 6. Configure Security Rules
In Firestore Console > Rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /analytics/{document} {
      allow read, write: if true;
    }
    match /admin/{document} {
      allow read: if true;
    }
  }
}
```

### 7. Test Firebase Connection

Create `test_connection.py` in `websiteanalytics/firebase/`:

```python
# test_connection.py
from firebase_config import db

def test_connection():
    try:
        # Test Firestore connection
        test_ref = db.collection("test").document("connection")
        test_ref.set({"status": "connected", "timestamp": "test"})
        
        # Read back the data
        doc = test_ref.get()
        if doc.exists:
            print("✅ Firebase connection successful!")
            print(f"Test data: {doc.to_dict()}")
            
            # Clean up test document
            test_ref.delete()
            print("✅ Test document cleaned up")
        else:
            print("❌ Failed to read test document")
            
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")

if __name__ == "__main__":
    test_connection()
```

**Run connection test:**
```bash
cd websiteanalytics/firebase
python test_connection.py
```

### 8. Run the Application
```bash
# Navigate back to project root
cd ../..
reflex run
```

### 9. Access Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## 📱 Application Pages
- `/` - Home page with analytics tracking
- `/signin` - User authentication  
- `/signup` - User registration
- `/shop` - Sample e-commerce page with tracking
- `/analytics` - Admin dashboard with charts

## 🔧 Project Structure
```
webanalytics/
├── websiteanalytics/
│   ├── pages/
│   │   ├── home.py
│   │   ├── signin.py
│   │   ├── signup.py
│   │   ├── shop.py
│   │   └── analyticalpage.py
│   ├── components/
│   │   └── navbar.py
│   ├── firebase/
│   │   ├── firebase_config.py
│   │   ├── serviceAccountKey.json (not in repo)
│   │   ├── setup_admin.py (helper script)
│   │   └── test_connection.py (helper script)
│   └── websiteanalytics.py
├── .gitignore
├── README.md
└── rxconfig.py
```

## 🔒 Security Best Practices

### Environment Variables (Optional)
Create `.env` file in project root:
```env
ADMIN_EMAIL=your-email@example.com
FIREBASE_PROJECT_ID=your-project-id
```

### Security Checklist
- ✅ `serviceAccountKey.json` is in `.gitignore`
- ✅ Admin passwords are hashed with SHA-256
- ✅ Firestore rules are configured properly
- ✅ No plain text passwords in code
- ✅ Test connection before deployment

## 🐛 Troubleshooting

### Common Issues
1. **Firebase Connection Error**
   - Check `serviceAccountKey.json` location
   - Verify project ID in Firebase Console
   - Run `test_connection.py`

2. **Admin Login Failed**
   - Verify admin document exists in Firestore
   - Check email matches document ID exactly
   - Confirm password hash is correct

3. **Permission Denied**
   - Update Firestore security rules
   - Check Firebase project settings

## 🚀 Ready to Use!
After setup, you can:
1. ✅ Register and authenticate users
2. ✅ Track real-time page visits and time spent
3. ✅ View interactive analytics dashboard
4. ✅ Filter data by users and pages
5. ✅ Monitor live user sessions with auto-refresh

---

**Built with ❤️ using Reflex and Firebase**
