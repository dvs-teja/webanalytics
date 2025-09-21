import reflex as rx

def navbar():
    # Define a professional color palette
    primary_color = "#34495e"  # Dark blue-gray for main links
    accent_color = "#3498db"   # A clean, professional blue for buttons
    hover_color = "#2c3e50"    # A slightly darker shade for hover effects
    bg_color = "#ecf0f1"       # Light gray for a clean background
    
    return rx.hstack(
        # Standard navigation links
        rx.link(
            "Home", 
            href="/home", 
            _hover={"color": hover_color}, 
            color=primary_color, 
            font_weight="medium"
        ),
        rx.link(
            "Shop", 
            href="/shop", 
            _hover={"color": hover_color}, 
            color=primary_color, 
            font_weight="medium"
        ),
        rx.link(
            "About", 
            href="/about", 
            _hover={"color": hover_color}, 
            color=primary_color, 
            font_weight="medium"
        ),
        rx.link(
            "Contact", 
            href="/contact", 
            _hover={"color": hover_color}, 
            color=primary_color, 
            font_weight="medium"
        ),
        
        rx.spacer(),
        
        rx.link(
            "Sign In",
            href="/signin",
            padding="8px 16px",
            bg=accent_color,
            color="white",
            border_radius="4px",
            _hover={"bg": "#2980b9"},
            font_weight="bold",
            transition="background-color 0.3s ease-in-out"
        ),
        rx.link(
            "Sign Up",
            href="/signup",
            padding="8px 16px",
            bg=accent_color,
            color="white",
            border_radius="4px",
            _hover={"bg": "#2980b9"},
            font_weight="bold",
            transition="background-color 0.3s ease-in-out"
        ),
        
        spacing="6",
        padding="16px 24px",
        bg=bg_color,
        width="100%",
        align="center",
        justify="start",
        shadow="sm"
    )