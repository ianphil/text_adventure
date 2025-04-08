from datetime import datetime
import json
from models import db

class GameState(db.Model):
    __tablename__ = 'game_states'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    current_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    save_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Game progress tracking
    progress_flags = db.Column(db.Text, default='{}')  # JSON string storing game flags
    turn_count = db.Column(db.Integer, default=0)
    
    # Relationships
    current_location = db.relationship('Location', foreign_keys=[current_location_id])
    story_memories = db.relationship('StoryMemory', backref='game_state', lazy=True)
    
    def __repr__(self):
        return f"<GameState {self.id} - Player {self.player_id}>"
    
    def get_flags(self):
        """Get progress flags as dictionary"""
        return json.loads(self.progress_flags)
    
    def set_flag(self, key, value):
        """Set a progress flag"""
        flags = self.get_flags()
        flags[key] = value
        self.progress_flags = json.dumps(flags)
    
    def increment_turn(self):
        """Increment the turn count"""
        self.turn_count += 1
        self.last_updated = datetime.utcnow()
    
    def to_dict(self):
        """Convert game state object to dictionary"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'current_location_id': self.current_location_id,
            'save_name': self.save_name,
            'turn_count': self.turn_count,
            'progress_flags': self.get_flags(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }