# Project Structure
.
├── game.py
├── narrative_engine
│   ├── game_state.py
│   ├── graph.py
│   └── __init__.py
├── pyproject.toml
├── README.md
├── tests
│   └── narrative_engine
│       ├── game_state_tests.py
│       └── graph_tests.py
└── uv.lock

## Tech stack
- uv (package manager, python manager)
- Flask
- Sqlite, SqlAlchemy
- Pytest is used for tests

## Constraints
- Always use `uv pip list` to understand what packages are installed
- Always use `uv add package_name` to install packages