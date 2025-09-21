import reflex as rx
from websiteanalytics.components.navbar import navbar

def home():
    return rx.vstack(
        navbar(),
        rx.heading("Welcome to Home Page"),
        rx.text("hi from the home page"),
        spacing="9",
        align="center"
    )
