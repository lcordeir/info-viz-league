from dash import Dash
from components.layout import create_layout
import components.callbacks  # Import registers callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "League of Legends Dashboard"
app.layout = create_layout()

if __name__ == "__main__":
    app.run_server(debug=True)
