import pytest
from flask import Flask
from narrative_engine.game_state import GameState, db, init_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    with app.app_context():
        init_app(app)
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

class TestGameState:
    def test_game_state_initialization(self, app):
        with app.app_context():
            # Test with default values
            state = GameState("start", "entrance")
            assert state.player_progress == "start"
            assert state.current_location == "entrance"
            assert state.inventory == []
            assert state.decision_history == []
            
            # Test with provided values
            state = GameState(
                "middle", 
                "forest", 
                inventory=["sword", "shield"], 
                decision_history=["fought_wolf"]
            )
            assert state.player_progress == "middle"
            assert state.current_location == "forest"
            assert state.inventory == ["sword", "shield"]
            assert state.decision_history == ["fought_wolf"]
    
    def test_save_and_load(self, app):
        with app.app_context():
            # Create and save a state
            state = GameState(
                player_progress="beginning",
                current_location="starting_room",
                inventory=["map"],
                decision_history=["entered_cave"]
            )
            state.save()
            
            state_id = state.id
            
            # Load the state and verify it matches
            loaded_state = GameState.load(state_id)
            assert loaded_state.player_progress == "beginning"
            assert loaded_state.current_location == "starting_room"
            assert loaded_state.inventory == ["map"]
            assert loaded_state.decision_history == ["entered_cave"]
    
    def test_update_progress(self, app):
        with app.app_context():
            # Create and save a state
            state = GameState(
                player_progress="beginning",
                current_location="starting_room"
            )
            state.save()
            
            state_id = state.id
            state.update_progress("middle")
            
            # Load and verify the update
            loaded_state = GameState.load(state_id)
            assert loaded_state.player_progress == "middle"
    
    def test_update_location(self, app):
        with app.app_context():
            # Create and save a state
            state = GameState(
                player_progress="beginning",
                current_location="starting_room"
            )
            state.save()
            
            state_id = state.id
            state.update_location("forest_clearing")
            
            # Load and verify the update
            loaded_state = GameState.load(state_id)
            assert loaded_state.current_location == "forest_clearing"
    
    def test_add_item(self, app):
        with app.app_context():
            # Create and save a state
            state = GameState(
                player_progress="beginning",
                current_location="starting_room",
                inventory=["map"]
            )
            state.save()
            
            state_id = state.id
            state.add_item("sword")
            
            # Load and verify the update
            loaded_state = GameState.load(state_id)
            assert "map" in loaded_state.inventory
            assert "sword" in loaded_state.inventory
            assert len(loaded_state.inventory) == 2
    
    def test_add_decision(self, app):
        with app.app_context():
            # Create and save a state
            state = GameState(
                player_progress="beginning",
                current_location="starting_room",
                decision_history=["entered_cave"]
            )
            state.save()
            
            state_id = state.id
            state.add_decision("fought_troll")
            
            # Load and verify the update
            loaded_state = GameState.load(state_id)
            assert "entered_cave" in loaded_state.decision_history
            assert "fought_troll" in loaded_state.decision_history
            assert len(loaded_state.decision_history) == 2