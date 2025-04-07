# Text Adventure Game

A narrative-driven text adventure game with a Flask API backend. The game uses a narrative graph structure to create an interactive story that players can navigate through text commands.

## Features

- Flask-based RESTful API
- Narrative graph for story progression
- Command parsing system
- Event system for reactive world elements
- Persistent game state using SQLAlchemy
- HTTP scripts for API testing

## Prerequisites

- Python 3.11+
- uv (package manager)

## Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd text_adventure
   ```

2. Install dependencies using uv
   ```bash
   uv sync
   ```

## Running the Game

1. Start the Flask server
   ```bash
   uv run game.py
   ```

2. The server will start on `http://localhost:5000`

## How to Play

The game is played through API calls. You can use the provided HTTP scripts in the `scripts/` directory with tools like REST Client for VS Code, Postman, or curl.

### Game Flow:

1. **Initialize a new game**
   - Use `scripts/init_game.http`
   - This will return a game state ID

2. **Check your current state**
   - Use `scripts/get_state.http`
   - Replace the state ID in the URL with your game state ID
   - This shows your current location, available exits, items, and inventory

3. **Send commands**
   - Use `scripts/send_command.http`
   - Replace the state ID and customize the command in the request body
   - Example commands: "go north", "go south", "look around"

4. **Pick up items**
   - Use `scripts/pickup_item.http`
   - Replace the state ID and item name in the URL
   - This adds the item to your inventory and may trigger events

5. **Use movement shortcuts**
   - Use `scripts/move_direction.http`
   - Replace the state ID and direction in the URL

### Event System

The game includes an event system that reacts to changes in the game state. Events are triggered automatically when certain conditions are met (like being in a specific location with a specific item).

#### Example: Door Event

1. Navigate to the treasure room
2. Pick up the key
3. Go to the hallway
4. The door event will automatically trigger, revealing a secret room
5. Use the new "door" exit to enter the secret room

To test this workflow, use `scripts/test_door_event.http`

### Example Gameplay Flow:

1. Initialize game (GET `/`)
2. Check state (GET `/state/1`)
3. Move to cave interior (POST `/command/1` with `{"command": "go forward"}`)
4. Check new state (GET `/state/1`)
5. Pick up an item (POST `/pickup/1/stone`)
6. Continue exploring by moving deeper (POST `/command/1` with `{"command": "go deeper"}`)

## Project Structure

```
.
├── game.py                    # Main Flask application
├── narrative_engine/          # Game engine components
│   ├── __init__.py
│   ├── commands.py            # Command parsing and handling
│   ├── events.py              # Event system for reactive world elements
│   ├── game_state.py          # Game state management
│   └── graph.py               # Narrative graph structure
├── scripts/                   # HTTP request scripts for testing
│   ├── init_game.http         # Initialize a new game
│   ├── get_state.http         # Get current game state
│   ├── send_command.http      # Send commands to the game
│   ├── pickup_item.http       # Pick up items in the current location
│   ├── move_direction.http    # Use legacy movement endpoint
│   └── test_door_event.http   # Demonstrate the door event workflow
├── instance/                  # SQLite database storage
│   └── game_state.db
└── tests/                     # Test cases
    └── narrative_engine/
        ├── commands_tests.py
        ├── events_tests.py
        ├── game_state_tests.py
        └── graph_tests.py
```

## Development

To run tests:
```bash
pytest
```

## Extending the Game

To extend the game, you can:
1. Add new nodes to the narrative graph in `game.py`
2. Create new command types in `narrative_engine/commands.py`
3. Define new events in `narrative_engine/events.py`
4. Enhance the game state functionality in `narrative_engine/game_state.py`