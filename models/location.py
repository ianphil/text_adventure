from models import db
import json

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_type = db.Column(db.String(50))  # e.g., indoor, outdoor, dungeon
    
    # JSON string storing exit directions and their destination location IDs
    exits = db.Column(db.Text, default='{}')  
    
    # AI generation properties
    ai_generation_enabled = db.Column(db.Boolean, default=False)
    ai_constraints = db.Column(db.Text)  # JSON string storing constraints for AI generation
    ai_required_elements = db.Column(db.Text)  # JSON string storing required elements
    ai_tone = db.Column(db.String(50))  # e.g., suspenseful, peaceful, mysterious
    
    # Relationships
    items = db.relationship('Item', backref='location', lazy=True)
    actions = db.relationship('Action', backref='location', lazy=True)
    
    def __repr__(self):
        return f"<Location {self.name}>"
    
    def get_exits(self):
        """Get exits as dictionary"""
        return json.loads(self.exits)
    
    def set_exit(self, direction, location_id):
        """Set an exit direction"""
        exits_dict = self.get_exits()
        exits_dict[direction] = location_id
        self.exits = json.dumps(exits_dict)
    
    def get_ai_constraints(self):
        """Get AI constraints as list"""
        if not self.ai_constraints:
            return []
        return json.loads(self.ai_constraints)
    
    def get_ai_required_elements(self):
        """Get AI required elements as list"""
        if not self.ai_required_elements:
            return []
        return json.loads(self.ai_required_elements)
    
    def to_dict(self):
        """Convert location object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location_type': self.location_type,
            'exits': self.get_exits(),
            'ai_generation_enabled': self.ai_generation_enabled,
            'ai_constraints': self.get_ai_constraints(),
            'ai_required_elements': self.get_ai_required_elements(),
            'ai_tone': self.ai_tone,
            'items': [item.to_dict() for item in self.items],
            'actions': [action.to_dict() for action in self.actions]
        }