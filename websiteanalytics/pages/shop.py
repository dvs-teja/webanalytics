import reflex as rx 
from websiteanalytics.components.navbar import navbar
from websiteanalytics.pages.signin import SigninState
from websiteanalytics.pages.analyticalpage import AnalyticsState

def shop():
    return rx.cond(
        SigninState.is_authenticated,
        rx.vstack(
            navbar(),
            rx.heading("Shop"),
            rx.text("This is the shop page. Accessed login successfully."),
            spacing="4",
            align="center",
            # Start tracking when this page loads
            on_mount=lambda: AnalyticsState.start_page_tracking("shop", SigninState.email)
        ),
        rx.vstack(
            navbar(),
            rx.heading("Access Denied"),
            rx.text("Please sign in to access the shop page."),
            spacing="4",
            align="center"
        )
    )
