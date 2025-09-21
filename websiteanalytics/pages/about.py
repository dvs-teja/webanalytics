import reflex as rx
from websiteanalytics.components.navbar import navbar


def about():
    return rx.vstack(
        navbar(),
        rx.heading("About"),
        rx.text("This is the about page."),
        spacing="4",
        align="center"
    )




