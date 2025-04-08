from datetime import datetime
from models import db

class StoryMemory(db.Model):
    __tablename__ = 'story_memories'
    
    id = db.Column(db.Integer, primary_key=True)
    game_state_id = db.Column(db.Integer, db.ForeignKey('game_states.id'), nullable=False)
    memory_text = db.Column(db.Text, nullable=False)
    
    # Memory metadata
    importance = db.Column(db.Integer, default=1)  # 1-10 scale of importance
    memory_type = db.Column(db.String(50))  # e.g., player_action, discovery, character_interaction
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Related game elements
    related_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    related_item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    # For organizing memories
    tags = db.Column(db.Text)  # JSON list of tags
    
    def __repr__(self):
        return f"<StoryMemory {self.id} - {self.memory_type}>"
    
    def to_dict(self):
        """Convert story memory object to dictionary"""
        import json
        memory_tags = []
        if self.tags:
            memory_tags = json.loads(self.tags)
            
        return {
            'id': self.id,
            'game_state_id': self.game_state_id,
            'memory_text': self.memory_text,
            'importance': self.importance,
            'memory_type': self.memory_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'related_location_id': self.related_location_id,
            'related_item_id': self.related_item_id,
            'tags': memory_tags
        }