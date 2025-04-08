from models import db
import json

class Action(db.Model):
    __tablename__ = 'actions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    
    # Next location or action to trigger
    next_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    next_action_name = db.Column(db.String(100))
    
    # Requirements to perform action
    requires_items = db.Column(db.Text)  # JSON list of required item IDs
    requires_flags = db.Column(db.Text)  # JSON dict of required game flags
    
    # Action effects
    grants_items = db.Column(db.Text)  # JSON list of granted item IDs
    sets_flags = db.Column(db.Text)  # JSON dict of flags to set
    
    def __repr__(self):
        return f"<Action {self.name} at {self.location_id}>"
    
    def get_required_items(self):
        """Get required items as list"""
        if not self.requires_items:
            return []
        return json.loads(self.requires_items)
    
    def get_required_flags(self):
        """Get required flags as dictionary"""
        if not self.requires_flags:
            return {}
        return json.loads(self.requires_flags)
    
    def get_granted_items(self):
        """Get granted items as list"""
        if not self.grants_items:
            return []
        return json.loads(self.grants_items)
    
    def get_set_flags(self):
        """Get flags to set as dictionary"""
        if not self.sets_flags:
            return {}
        return json.loads(self.sets_flags)
    
    def to_dict(self):
        """Convert action object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location_id': self.location_id,
            'next_location_id': self.next_location_id,
            'next_action_name': self.next_action_name,
            'requires_items': self.get_required_items(),
            'requires_flags': self.get_required_flags(),
            'grants_items': self.get_granted_items(),
            'sets_flags': self.get_set_flags()
        }