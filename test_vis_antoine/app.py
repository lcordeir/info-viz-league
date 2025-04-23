from dash import Dash
from test_vis_antoine.components.main_menu.main_menu import create_layout
import test_vis_antoine.components.main_menu.main_menu_callbacks  # Import registers callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "League of Legends Dashboard"
app.layout = create_layout()

if __name__ == "__main__":
    app.run(debug=True)