# Project Structure
```
.
├── game.py                    # Main Flask application
├── narrative_engine/          # Game engine components
│   ├── __init__.py
│   ├── ai_generator.py        # AI narrative generation
│   ├── commands.py            # Command parsing and handling
│   ├── events.py              # Event system for reactive world elements
│   ├── game_state.py          # Game state management
│   ├── graph.py               # Narrative graph structure
│   └── narrative_memory.py    # Persistent memory of game events
├── scripts/                   # HTTP request scripts for testing
│   ├── init_game.http         # Initialize a new game
│   ├── get_state.http         # Get current game state
│   ├── send_command.http      # Send commands to the game
│   ├── pickup_item.http       # Pick up items in the current location
│   ├── move_direction.http    # Use legacy movement endpoint
│   └── test_door_event.http   # Demonstrate the door event workflow
├── env.sample                 # Sample environment variables file
├── instance/                  # SQLite database storage
│   └── game_state.db
└── tests/                     # Test cases
    └── narrative_engine/
        ├── ai_generator_tests.py
        ├── commands_tests.py
        ├── events_tests.py
        ├── game_state_tests.py
        ├── graph_tests.py
        └── narrative_memory_tests.py
```

## Tech stack
- uv (package manager, python manager)
- Flask
- Sqlite, SqlAlchemy
- Pytest is used for tests

## Constraints
- Always use `uv pip list` to understand what packages are installed
- Always use `uv add package_name` to install packages