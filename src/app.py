from dash import Dash
from layout.main_menu import create_layout
import layout.callbacks  # Import registers callbacks
import layout.filters.callbacks
import layout.map.callbacks
import layout.plots.callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "League of Legends Dashboard"
app.layout = create_layout()

if __name__ == "__main__":
    app.run(debug=True)
