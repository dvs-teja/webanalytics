import reflex as rx
from websiteanalytics.components.navbar import navbar
from websiteanalytics.pages.signin import SigninState
from websiteanalytics.pages.analyticalpage import AnalyticsState

def about():
    return rx.cond(
        SigninState.is_authenticated,
        rx.vstack(
            navbar(),
            rx.heading("About"),
            rx.text("This is the about page. Access granted."),
            spacing="4",
            align="center",
            # Start tracking when this page loads
            on_mount=lambda: AnalyticsState.start_page_tracking("about", SigninState.email)
        ),
        rx.vstack(
            navbar(),
            rx.heading("Access Denied"),
            rx.text("Please sign in to access the about page."),
            spacing="4",
            align="center"
        ) 
    )




