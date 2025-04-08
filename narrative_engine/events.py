# narrative_engine/events.py

class Event:
    def __init__(self, name, condition, action):
        """
        :param name: A string identifier for the event.
        :param condition: A function that takes game_state and returns True if the event should trigger.
        :param action: A function that takes game_state and performs the event action.
        """
        self.name = name
        self.condition = condition
        self.action = action

    def check_and_execute(self, game_state):
        """
        Checks if the event's condition is met and executes the action if so.
        :param game_state: The current game state (e.g., a dict or custom object).
        :return: True if the event was triggered and executed, False otherwise.
        """
        if self.condition(game_state):
            self.action(game_state)
            return True
        return False

class EventHandler:
    def __init__(self):
        self.events = []

    def register_event(self, event):
        """
        Registers a new event to be processed.
        :param event: An instance of Event.
        """
        self.events.append(event)

    def process_events(self, game_state):
        """
        Processes all registered events by checking their conditions against the game state.
        :param game_state: The current game state.
        :return: A list of names of the events that were triggered.
        """
        triggered_events = []
        for event in self.events:
            if event.check_and_execute(game_state):
                triggered_events.append(event.name)
        return triggered_events

# Example: Event trigger for opening a door

def door_condition(game_state):
    """
    Check if the player is in the hallway, has a key, and the door is not already open.
    :param game_state: GameState object with attributes like 'current_location', 'inventory'.
    """
    return (
        game_state.current_location == 'hallway' and 
        'key' in game_state.inventory and 
        not getattr(game_state, 'door_open', False)
    )

def door_action(game_state):
    """
    Update the game state to mark the door as open and add a new exit.
    :param game_state: GameState object.
    """
    # Set the door flag to open
    if hasattr(game_state, 'flags') and isinstance(game_state.flags, dict):
        game_state.flags['door_open'] = True
    
    # Add a new exit called 'door' that leads to a secret room
    if hasattr(game_state, 'exits') and isinstance(game_state.exits, dict):
        game_state.exits['door'] = 'secret_room'

    # We need to update the graph to add the new exit
    from narrative_engine.graph import load_graph_from_json
    graph = load_graph_from_json(game_state.narrative_graph)
    hallway_node = graph.nodes.get('hallway')
    if hallway_node:
        hallway_node.exits['door'] = 'secret_room'
    from narrative_engine.graph import graph_to_json
    game_state.narrative_graph = graph_to_json(graph)

    # Add to narrative memory
    if hasattr(game_state, 'narrative_memory'):
        import json
        memory_events = []
        if game_state.narrative_memory:
            try:
                memory_events = json.loads(game_state.narrative_memory) if isinstance(game_state.narrative_memory, str) else game_state.narrative_memory
            except json.JSONDecodeError:
                memory_events = []
        memory_events.append("The ancient key glows briefly. With a loud creak, the door in the hallway slowly opens, revealing a passage beyond.")
        game_state.narrative_memory = json.dumps(memory_events) if not isinstance(game_state.narrative_memory, list) else memory_events

    # Save the changes
    game_state.save()

# Create an event instance for opening a door
open_door_event = Event("Open Door", door_condition, door_action)
