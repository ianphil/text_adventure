from models import db

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))  # If item is in player inventory
    
    portable = db.Column(db.Boolean, default=True)
    visible = db.Column(db.Boolean, default=True)
    unique_id = db.Column(db.String(100), unique=True)  # For identifying specific items
    
    # For AI-generated descriptions
    ai_description_variations = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<Item {self.name}>"
    
    def to_dict(self):
        """Convert item object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location_id': self.location_id,
            'player_id': self.player_id,
            'portable': self.portable,
            'visible': self.visible,
            'unique_id': self.unique_id,
            'ai_description_variations': self.ai_description_variations
        }