# app.py

from flask import Flask, jsonify, request, render_template
from narrative_engine.game_state import init_app, GameState
from narrative_engine.graph import NarrativeGraph, Node, load_graph_from_json
from narrative_engine.commands import Command, MoveCommand, parse_command, COMMAND_MAPPINGS
import json
import datetime
import os

app = Flask(__name__)

# Ensure instance directory exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
    print(f"Created instance directory at: {instance_path}")

# Use absolute path for database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "game_state.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the game state module with the Flask app
init_app(app)

# Create a simple example narrative graph
def create_sample_graph():
    graph = NarrativeGraph()
    
    # Create some nodes
    entrance = Node("entrance", "You are at the entrance of a dark cave. A cool breeze flows from inside.", 
                    exits={"forward": "cave_interior"}, 
                    items=["torch"], 
                    actions={"light torch": "You light the torch, illuminating the area around you."})
    
    interior = Node("cave_interior", "You're inside the cave. Water drips from stalactites above.",
                   exits={"back": "entrance", "deeper": "treasure_room"},
                   items=["stone"],
                   actions={"examine walls": "You notice strange markings on the walls."})
    
    treasure = Node("treasure_room", "A small chamber with an old chest in the corner.",
                   exits={"exit": "cave_interior"},
                   items=["chest", "skeleton"],
                   actions={"open chest": "The chest contains a golden key!"})
    
    graph.add_node(entrance)
    graph.add_node(interior)
    graph.add_node(treasure)
    
    return graph

# Convert graph to JSON for storage
def graph_to_json(graph):
    nodes_dict = {}
    for node_id, node in graph.nodes.items():
        nodes_dict[node_id] = {
            "description": node.description,
            "exits": node.exits,
            "items": node.items,
            "actions": node.actions
        }
    return json.dumps({"nodes": nodes_dict})

@app.route('/')
def index():
    # Create a sample narrative graph
    game_graph = create_sample_graph()
    
    # Serialize the graph for storage
    graph_json = graph_to_json(game_graph)
    
    # Create or update game state with the graph
    game_state = GameState(
        player_progress="Level 1", 
        current_location="entrance",
        inventory=["map"],
        decision_history=[{"action": "start_game", "timestamp": "2025-04-07T12:00:00"}]
    )
    
    # Store the narrative graph in a custom field
    game_state.narrative_graph = graph_json
    game_state.save()
    
    return f"Game initialized with ID: {game_state.id}"

@app.route('/state/<int:state_id>')
def show_state(state_id):
    # Load game state
    game_state = GameState.load(state_id)
    if not game_state:
        return jsonify({"error": "Game state not found"}), 404
    
    # Load the narrative graph
    graph = load_graph_from_json(game_state.narrative_graph)
    
    # Get current location data
    current_node = graph.nodes.get(game_state.current_location)
    if not current_node:
        return jsonify({"error": "Invalid location in game state"}), 500
    
    # Return the game state information
    return jsonify({
        "game_id": game_state.id,
        "progress": game_state.player_progress,
        "location": {
            "id": current_node.node_id,
            "description": current_node.description,
            "exits": current_node.exits,
            "items": current_node.items
        },
        "inventory": game_state.inventory,
        "history": game_state.decision_history
    })

# Command execution handler
def execute_command(game_state, command_obj, graph):
    """
    Executes a command and updates the game state accordingly
    
    :param game_state: The current GameState object
    :param command_obj: A Command object to execute
    :param graph: The narrative graph for the current game
    :return: dict with result information
    """
    if isinstance(command_obj, MoveCommand):
        direction = command_obj.direction
        current_node = graph.nodes.get(game_state.current_location)
        
        # Check if the direction is valid
        if direction not in current_node.exits:
            return {"error": f"Cannot go {direction} from here", "valid_exits": current_node.exits}
        
        # Get the new location
        new_location = current_node.exits[direction]
        
        # Update the game state
        game_state.update_location(new_location)
        game_state.add_decision({
            "action": f"move_{direction}", 
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "message": f"Moved {direction} to {new_location}",
            "new_location": new_location
        }
    
    # Handle other command types as they are added
    return {"error": "Command type not supported yet"}

@app.route('/command/<int:state_id>', methods=['POST'])
def process_command(state_id):
    """
    Process a natural language command from the player
    """
    # Check for command in request
    if not request.json or 'command' not in request.json:
        return jsonify({"error": "Missing command parameter"}), 400
    
    command_text = request.json['command']
    
    # Parse the command
    command_obj = parse_command(command_text)
    if not command_obj:
        return jsonify({"error": f"I don't understand '{command_text}'"}), 400
        
    # Load game state
    game_state = GameState.load(state_id)
    if not game_state:
        return jsonify({"error": "Game state not found"}), 404
    
    # Load the narrative graph
    graph = load_graph_from_json(game_state.narrative_graph)
    
    # Execute the command
    result = execute_command(game_state, command_obj, graph)
    
    # Check for errors
    if "error" in result:
        return jsonify(result), 400
        
    # Save the updated game state
    game_state.save()
    
    return jsonify(result)

@app.route('/move/<int:state_id>/<direction>')
def move(state_id, direction):
    """Legacy endpoint that now uses the command pattern internally"""
    # Load game state
    game_state = GameState.load(state_id)
    if not game_state:
        return jsonify({"error": "Game state not found"}), 404
    
    # Create and execute a move command
    command = MoveCommand(direction)
    
    # Load the narrative graph
    graph = load_graph_from_json(game_state.narrative_graph)
    
    # Execute the command
    result = execute_command(game_state, command, graph)
    
    # Check for errors
    if "error" in result:
        return jsonify(result), 400
        
    # Save the updated game state
    game_state.save()
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
