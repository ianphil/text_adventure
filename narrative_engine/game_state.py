from models import db
from sqlalchemy.types import TypeDecorator, TEXT
import json

class JSONEncodedDict(TypeDecorator):
    """A custom type to store JSON-encoded dictionaries."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            value = {}
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            value = {}
        return json.loads(value)

class GameState(db.Model):
    __tablename__ = 'game_state'
    id = db.Column(db.Integer, primary_key=True)
    player_progress = db.Column(db.String(100), nullable=False)
    current_location = db.Column(db.String(100), nullable=False)
    inventory = db.Column(JSONEncodedDict, nullable=False, default=[])
    decision_history = db.Column(JSONEncodedDict, nullable=False, default=[])
    narrative_graph = db.Column(JSONEncodedDict, nullable=True)
    narrative_memory = db.Column(JSONEncodedDict, nullable=True)

    def __init__(self, player_progress, current_location, inventory=None, decision_history=None, narrative_graph=None, narrative_memory=None):
        self.player_progress = player_progress
        self.current_location = current_location
        self.inventory = inventory if inventory is not None else []
        self.decision_history = decision_history if decision_history is not None else []
        self.narrative_graph = narrative_graph
        self.narrative_memory = narrative_memory

    def save(self):
        """Save the current game state to the database."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def load(cls, state_id):
        """Load a game state from the database by its ID."""
        return cls.query.get(state_id)

    def update_progress(self, progress):
        self.player_progress = progress
        self.save()

    def update_location(self, new_location):
        self.current_location = new_location
        self.save()

    def add_item(self, item):
        """Add an item to the inventory and save changes."""
        # Create a new list with the existing items plus the new one
        # This ensures SQLAlchemy detects the change
        current_inventory = self.inventory.copy()
        current_inventory.append(item)
        self.inventory = current_inventory
        self.save()

    def add_decision(self, decision):
        """Add a decision to the history and save changes."""
        # Create a new list with the existing decisions plus the new one
        # This ensures SQLAlchemy detects the change
        current_decisions = self.decision_history.copy()
        current_decisions.append(decision)
        self.decision_history = current_decisions
        self.save()

def init_app(app):
    """Initialize the module with the Flask app configuration."""
    db.init_app(app)
    with app.app_context():
        db.create_all()