import reflex as rx
from websiteanalytics.components.navbar import navbar
import hashlib
from ..firebase.firebase_config import db

# Your state class
class SigninState(rx.State):
    email: str = ""
    password: str = ""
    message: str = ""

    def check_user(self):
        if not (self.email and self.password):
            self.message = "All fields are required!"
            return
        user_ref = db.collection("users")  # your Firestore collection
        users = user_ref.where("email", "==", self.email).get()

        if not users:
            self.message = "No user found with this email!"
            return

        hashed_password = hashlib.sha256(self.password.encode()).hexdigest()
        user_data = users[0].to_dict()

        if user_data.get("password") != hashed_password:
            self.message = "Invalid email or password!"
            return

        self.message = "Sign in successful!"

def signin_page():
    return rx.vstack(
        navbar(),
        rx.input(
            placeholder="Email",
            value=SigninState.email,
            on_change=SigninState.set_email,
        ),
        rx.input(
            placeholder="Password",
            type_="password",
            value=SigninState.password,
            on_change=SigninState.set_password,
        ),
        rx.button("Sign In", on_click=SigninState.check_user),
        rx.text(SigninState.message, color="red"),  # <-- Use the state variable directly
    )
