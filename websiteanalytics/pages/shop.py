import reflex as rx 
from websiteanalytics.components.navbar import navbar


def shop():

  return rx.vstack(
    navbar(),
    rx.text("hi from the shop page")
  )
