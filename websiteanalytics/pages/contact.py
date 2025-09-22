import reflex as rx


from websiteanalytics.components.navbar import navbar
from websiteanalytics.pages.signin import SigninState


def contact():
    return rx.cond(
        SigninState.is_authenticated,
        rx.vstack(
            navbar(),
            rx.heading("Contact"),
            rx.text("This is the contact page.accessed login successfully."),
            spacing="4",
            align="center"
        ),
        rx.vstack(
            navbar(),
            rx.heading("Access Denied"),
            rx.text("Please sign in to access the contact page."),
            spacing="4",
            align="center"
          )
    )