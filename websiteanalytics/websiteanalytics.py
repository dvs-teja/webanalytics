import reflex as rx
from websiteanalytics.pages.home import home
from websiteanalytics.pages.shop import shop
from websiteanalytics.pages.signin import signin_page as signin
from websiteanalytics.pages.signup import signup
from websiteanalytics.components.navbar import navbar
from websiteanalytics.pages.about import about
from websiteanalytics.pages.contact import contact
def index():
    return rx.vstack(
        navbar(),
        rx.heading("Welcome to E-commerce!"),
        rx.text("Use the navbar to explore pages"),
    )

app = rx.App()
app.add_page(index, route="/")
app.add_page(home, route="/home")
app.add_page(shop, route="/shop")
app.add_page(about, route="/about")
app.add_page(contact, route="/contact")
app.add_page(signin, route="/signin")
app.add_page(signup, route="/signup")
