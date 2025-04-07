# app.py

from flask import Flask
from narrative_engine.game_state import init_app, GameState

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_state.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the game state module with the Flask app
init_app(app)

@app.route('/')
def index():
    # Example usage: create a new game state if one doesn't exist
    new_state = GameState(player_progress="Level 1", current_location="start")
    new_state.save()
    return f"GameState created with ID: {new_state.id}"

if __name__ == '__main__':
    app.run(debug=True)
