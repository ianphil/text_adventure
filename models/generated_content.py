from datetime import datetime
from models import db

class GeneratedContent(db.Model):
    __tablename__ = 'generated_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)  # e.g., location_description, dialogue
    content = db.Column(db.Text, nullable=False)
    
    # Related game elements
    game_state_id = db.Column(db.Integer, db.ForeignKey('game_states.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    
    # Generation metadata
    prompt_used = db.Column(db.Text)
    parameters_used = db.Column(db.Text)  # JSON string of parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Caching and versioning
    cache_key = db.Column(db.String(255))
    version = db.Column(db.Integer, default=1)
    
    # Quality feedback (if implemented)
    quality_rating = db.Column(db.Integer)
    
    def __repr__(self):
        return f"<GeneratedContent {self.id} - {self.content_type}>"
    
    def to_dict(self):
        """Convert generated content object to dictionary"""
        import json
        parameters = {}
        if self.parameters_used:
            parameters = json.loads(self.parameters_used)
            
        return {
            'id': self.id,
            'content_type': self.content_type,
            'content': self.content,
            'game_state_id': self.game_state_id,
            'location_id': self.location_id,
            'prompt_used': self.prompt_used,
            'parameters_used': parameters,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'cache_key': self.cache_key,
            'version': self.version,
            'quality_rating': self.quality_rating
        }