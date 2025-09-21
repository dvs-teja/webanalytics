import reflex as rx


from websiteanalytics.components.navbar import navbar



def contact():
    return rx.vstack(
        navbar(),
        rx.heading("Contact Us"),
        rx.text("This is the contact page."),
        spacing="4",
        align="center"
    )