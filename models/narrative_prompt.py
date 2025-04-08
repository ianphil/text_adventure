from models import db

class NarrativePrompt(db.Model):
    __tablename__ = 'narrative_prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    prompt_template = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    prompt_type = db.Column(db.String(50))  # e.g., location_description, character_dialogue
    
    # Parameters for injection
    required_parameters = db.Column(db.Text)  # JSON list of required parameters
    
    # Quality control
    max_tokens = db.Column(db.Integer, default=500)
    temperature = db.Column(db.Float, default=0.7)
    
    def __repr__(self):
        return f"<NarrativePrompt {self.name}>"
    
    def to_dict(self):
        """Convert prompt object to dictionary"""
        import json
        required_params = []
        if self.required_parameters:
            required_params = json.loads(self.required_parameters)
            
        return {
            'id': self.id,
            'name': self.name,
            'prompt_template': self.prompt_template,
            'description': self.description,
            'prompt_type': self.prompt_type,
            'required_parameters': required_params,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }