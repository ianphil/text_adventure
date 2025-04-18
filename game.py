# app.py

from flask import Flask, jsonify, request, render_template
from narrative_engine.game_state import init_app, GameState
from narrative_engine.graph import NarrativeGraph, Node, load_graph_from_json, graph_to_json
from narrative_engine.commands import Command, MoveCommand, parse_command, COMMAND_MAPPINGS
from narrative_engine.events import Event, EventHandler, open_door_event
from narrative_engine.ai_generator import init_app as init_ai, generate_dynamic_narrative
from narrative_engine.narrative_memory import NarrativeMemory
import json
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Ensure instance directory exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
    print(f"Created instance directory at: {instance_path}")

# Use absolute path for database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "game_state.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# AI Generator Module Configuration
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', 'fake-key-for-development')
app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.config['REDIS_CACHING_ENABLED'] = False  # Disable Redis caching as requested

# Initialize the game state module with the Flask app
init_app(app)

# Initialize the AI generator module
init_ai(app)

# Create and configure the event handler
event_handler = EventHandler()
# Register the open door event
event_handler.register_event(open_door_event)

# Create a sample hallway-door event to demonstrate event system
def create_hallway_node():
    return Node(
        "hallway",
        "You are in a long hallway with a locked door at the end.",
        exits={"back": "cave_interior"},
        items=[]
    )

# Create a secret room node for the door event
def create_secret_room_node():
    return Node(
        "secret_room",
        "You've found a hidden chamber with ancient treasures!",
        exits={"exit": "hallway"},
        items=["gold", "jewels"]
    )

# Create a simple example narrative graph
def create_sample_graph():
    graph = NarrativeGraph()
    
    # Create some nodes
    entrance = Node("entrance", "You are at the entrance of a dark cave. A cool breeze flows from inside.", 
                    exits={"forward": "cave_interior"}, 
                    items=["torch"], 
                    actions={"light torch": "You light the torch, illuminating the area around you."})
    
    interior = Node("cave_interior", "You're inside the cave. Water drips from stalactites above.",
                   exits={"back": "entrance", "deeper": "treasure_room", "hallway": "hallway"},
                   items=["stone"],
                   actions={"examine walls": "You notice strange markings on the walls."})
    
    treasure = Node("treasure_room", "A small chamber with an old chest in the corner.",
                   exits={"exit": "cave_interior"},
                   items=["chest", "skeleton", "key"],
                   actions={"open chest": "The chest contains a golden key!"})
    
    hallway = create_hallway_node()
    secret_room = create_secret_room_node()
    
    graph.add_node(entrance)
    graph.add_node(interior)
    graph.add_node(treasure)
    graph.add_node(hallway)
    graph.add_node(secret_room)
    
    return graph


@app.route('/')
def index():
    # Create a sample narrative graph
    game_graph = create_sample_graph()
    
    # Serialize the graph for storage
    graph_json = graph_to_json(game_graph)
    
    # Create narrative memory for the game
    memory = NarrativeMemory()
    
    # Generate dynamic introduction narrative
    intro_narrative = generate_dynamic_narrative(
        "cave entrance", 
        "mysterious", 
        "darkness, breeze, stone walls",
        memory
    )
    
    # Create or update game state with the graph
    game_state = GameState(
        player_progress="Level 1", 
        current_location="entrance",
        inventory=["map"],
        decision_history=[{"action": "start_game", "timestamp": "2025-04-07T12:00:00"}]
    )
    
    # Store the narrative graph and memory in custom fields
    game_state.narrative_graph = graph_json
    game_state.narrative_memory = json.dumps([event for event in memory.events])
    game_state.save()
    
    return jsonify({
        "game_id": game_state.id,
        "intro_narrative": intro_narrative,
        "message": f"Game initialized with ID: {game_state.id}"
    })

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
    
    # Check for potential events that could trigger in this state
    potential_events = []
    for event in event_handler.events:
        if event.condition(game_state):
            potential_events.append(event.name)
    
    # Load narrative memory
    memory = NarrativeMemory()
    if hasattr(game_state, 'narrative_memory') and game_state.narrative_memory:
        try:
            memory_events = json.loads(game_state.narrative_memory)
            for event in memory_events:
                memory.add_event(event)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse narrative memory from game state")
    
    # Generate dynamic description for current location
    location_narrative = generate_dynamic_narrative(
        current_node.node_id,
        "descriptive",
        ", ".join(current_node.items) if current_node.items else "ambient details",
        memory
    )
    
    # Return the game state information with enhanced narrative
    return jsonify({
        "game_id": game_state.id,
        "progress": game_state.player_progress,
        "location": {
            "id": current_node.node_id,
            "description": current_node.description,
            "narrative": location_narrative,
            "exits": current_node.exits,
            "items": current_node.items
        },
        "inventory": game_state.inventory,
        "history": game_state.decision_history,
        "potential_events": potential_events
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
    command_result = {}
    
    # Load or initialize narrative memory
    memory = NarrativeMemory()
    if hasattr(game_state, 'narrative_memory') and game_state.narrative_memory:
        try:
            memory_events = json.loads(game_state.narrative_memory)
            for event in memory_events:
                memory.add_event(event)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse narrative memory from game state")
    
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
        
        # Add to narrative memory
        memory.add_event(f"You moved {direction} to the {new_location}.")
        
        # Get the new location node
        new_node = graph.nodes.get(new_location)
        
        # Generate dynamic transition narrative
        transition_narrative = generate_dynamic_narrative(
            new_location,
            "atmospheric",
            ", ".join(new_node.items) if new_node.items else "ambient details",
            memory
        )
        
        command_result = {
            "success": True,
            "message": f"Moved {direction} to {new_location}",
            "narrative": transition_narrative,
            "new_location": new_location
        }
    else:
        # Handle other command types as they are added
        return {"error": "Command type not supported yet"}
    
    # Save updated narrative memory to game state
    game_state.narrative_memory = json.dumps([event for event in memory.events])
    
    # Process events after command execution
    triggered_events = event_handler.process_events(game_state)
    if triggered_events:
        command_result["triggered_events"] = triggered_events
    
    return command_result

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

@app.route('/pickup/<int:state_id>/<item>', methods=['POST'])
def pickup_item(state_id, item):
    """
    Route to handle picking up an item in the current location
    """
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
    
    # Check if the item is in the current location
    if item not in current_node.items:
        return jsonify({"error": f"There is no {item} here to pick up"}), 400
    
    # Add item to inventory
    game_state.add_item(item)
    
    # Load or initialize narrative memory
    memory = NarrativeMemory()
    if hasattr(game_state, 'narrative_memory') and game_state.narrative_memory:
        try:
            memory_events = json.loads(game_state.narrative_memory)
            for event in memory_events:
                memory.add_event(event)
        except json.JSONDecodeError:
            app.logger.error("Failed to parse narrative memory from game state")
    
    # Add to narrative memory
    memory.add_event(f"You picked up the {item}.")
    
    # Generate dynamic item narrative
    item_narrative = generate_dynamic_narrative(
        item,
        "intriguing",
        f"{item}, texture, details",
        memory
    )
    
    # Save updated narrative memory to game state
    game_state.narrative_memory = json.dumps([event for event in memory.events])
    
    # Remove item from the location
    items = current_node.items.copy()
    items.remove(item)
    graph.update_node(current_node.node_id, items=items)
    
    # Update the narrative graph in the game state
    game_state.narrative_graph = graph_to_json(graph)
    game_state.save()
    
    # Process events after picking up the item
    triggered_events = event_handler.process_events(game_state)
    
    result = {
        "success": True,
        "message": f"You picked up the {item}",
        "narrative": item_narrative,
        "inventory": game_state.inventory
    }
    
    if triggered_events:
        result["triggered_events"] = triggered_events
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
