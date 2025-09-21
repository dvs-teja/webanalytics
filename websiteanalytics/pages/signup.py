import reflex as rx
from websiteanalytics.components.navbar import navbar
from ..firebase.firebase_config import db
import hashlib

class SignupState(rx.State):
    username: str = ""
    email: str = ""
    password: str = ""
    message: str = ""

    # Function to sign up user
    def signup_user(self):
        # Validate inputs
        if not (self.username and self.email and self.password):
            self.message = "All fields are required!"
            return
        
        # Reference to users collection
        user_ref = db.collection("users")
        
        # Check if user with email already exists
        existing_user = user_ref.where("email", "==", self.email).get()
        if existing_user:
            self.message = "User with this email already exists!"
            print(self.message)
            return

        # Hash the password
        hashed_password = hashlib.sha256(self.password.encode()).hexdigest()

        # Add new user to Firestore
        db.collection("users").add({
            "username": self.username,
            "email": self.email,
            "password": hashed_password
        })

        # Update message
        self.message = "User signed up successfully!"
        print(self.message)

        # Clear input fields
        self.username = ""
        self.email = ""
        self.password = ""

def signup():
    return rx.vstack(
        navbar(),
        rx.input(
            placeholder="Username",
            value=SignupState.username,
            on_change=SignupState.set_username
        ),
        rx.input(
            placeholder="Email",
            value=SignupState.email,
            on_change=SignupState.set_email
        ),
        rx.input(
            placeholder="Password",
            type_="password",
            value=SignupState.password,
            on_change=SignupState.set_password
        ),
        rx.button(
            "Sign Up",
            color_scheme="blue",
            margin_top="10px",
            on_click=SignupState.signup_user
        ),
        # Display messages dynamically
        rx.text(SignupState.message, color="red", margin_top="10px")
    )
