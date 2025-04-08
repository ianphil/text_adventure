from datetime import datetime
from models import db

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Player stats and attributes
    health = db.Column(db.Integer, default=100)
    max_health = db.Column(db.Integer, default=100)
    experience = db.Column(db.Integer, default=0)
    
    # Relationships
    game_states = db.relationship('GameState', backref='player', lazy=True)
    
    def __repr__(self):
        return f"<Player {self.username}>"
    
    def to_dict(self):
        """Convert player object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'health': self.health,
            'max_health': self.max_health,
            'experience': self.experience,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }