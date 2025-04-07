# Text Adventure Game - Technical Specification

## Project Overview

Create an interactive, web-based text adventure game with a modern UI using Python Flask backend and shadcn/ui components for the frontend. The game will present players with narrative text, allow them to make choices or enter commands, and progress through a branching storyline. A key feature of this game is AI-driven dynamic content generation within a predefined story framework, ensuring each player experiences a unique storyline.

## Tech Stack

### Backend

- **Python 3.10+**
- **Flask 2.3+**: Web framework
- **SQLite**: For game state persistence
- **Flask-SQLAlchemy**: ORM for database interactions
- **Flask-Session**: For session management
- **OpenAI API** or **Anthropic API**: For AI content generation
- **Redis**: For caching generated content

### Frontend

- **Next.js 14+**: Frontend framework
- **TypeScript**: For type safety
- **Tailwind CSS**: For styling
- **shadcn/ui**: Component library
- **Axios**: For API requests to the Flask backend

## Application Architecture

### Backend Components

1. **Game Engine**
    
    - Story graph management
    - Game state tracking
    - Command parsing
    - Event triggers
    - AI-driven content generation
2. **AI Narrative System**
    
    - LLM API integration (OpenAI, Anthropic, or similar)
    - Prompt template management
    - Content validation and filtering
    - Narrative memory and coherence tracking
    - Fallback content management
3. **API Endpoints**
    
    - `/api/game/start`: Initialize a new game
    - `/api/game/action`: Process player actions
    - `/api/game/save`: Save game state
    - `/api/game/load`: Load saved game
    - `/api/game/state`: Get current game state
4. **Data Models**
    
    - `Player`: Player information and stats
    - `GameState`: Current state of the game
    - `Location`: Game locations/scenes
    - `Item`: Interactive items in the game
    - `Action`: Possible actions for each scene
    - `NarrativePrompt`: Templates for AI content generation
    - `GeneratedContent`: Cached AI-generated content
    - `StoryMemory`: Important narrative events to maintain coherence

### Frontend Components

1. **Game Interface**
    
    - Text display area (shadcn/ui Card)
    - Command input (shadcn/ui Input)
    - Action buttons for choices (shadcn/ui Button)
    - Game menu (shadcn/ui DropdownMenu)
    - Inventory display (shadcn/ui Sheet)
2. **Pages**
    
    - Home/Start screen
    - Main game interface
    - Save/Load screen
    - Settings screen
    - About/Help screen

## Core Functionality

### Game Flow

1. Player starts a new game or loads a saved game
2. Server sends initial location description and available actions
3. Player inputs commands or selects from available actions
4. Server processes the action and updates game state
5. Updated game state is sent back to frontend
6. UI updates to reflect new game state
7. Process repeats until game end

### Command Parser

- Process natural language inputs like "go north", "take key", etc.
- Support for common abbreviations ("n" for "north", "i" for "inventory")
- Fuzzy matching for close commands
- Basic synonym recognition

### Game State Management

- Save/load functionality
- Persistent inventory
- Location tracking
- Game progress flags
- Character stats (if applicable)
- Decision history

## UI Design Requirements

### Main Game Screen

- Clean, distraction-free interface
- Dark mode by default with light mode toggle
- Fixed-width text container (70-80 characters per line)
- Scrollable history of past text
- Clear visual indication of available actions
- Command history accessible with up/down arrows
- Subtle animations for text appearance

### Visual Elements

- Custom typography for game text
- Consistent color scheme
- Minimal sound effects for key actions (optional)
- Simple transitions between scenes
- Visual feedback for successful/unsuccessful actions

## Development Guidelines

### Code Organization

- Modular architecture
- Clear separation between game logic and presentation
- Well-documented API between frontend and backend
- Configuration files for game content

### Game Content Structure

```json
{
  "locations": {
    "start": {
      "description": "You find yourself in a dimly lit room...",
      "exits": ["north", "east"],
      "items": ["lamp", "note"],
      "actions": {
        "read note": {"next": "read_note", "requires": ["note"]},
        "go north": {"next": "hallway"}
      },
      "ai_generation": {
        "enabled": true,
        "constraints": ["indoor", "mysterious"],
        "required_elements": ["clue_about_backstory"],
        "tone": "suspenseful"
      }
    },
    // Additional locations...
  },
  "items": {
    "lamp": {
      "description": "An old oil lamp, still functional.",
      "portable": true,
      "actions": ["light", "take", "drop"],
      "ai_description_variations": true
    },
    // Additional items...
  },
  "narrative_prompts": {
    "location_description": "Generate a detailed description of {location_type} with atmosphere {tone}. Include references to {required_elements} and ensure it connects to the player's previous actions regarding {relevant_history}.",
    "character_dialogue": "Create dialogue for a {character_type} character who knows about {knowledge_elements} and has the following traits: {character_traits}. The dialogue should reveal {revelation_level} information about {plot_element}."
  }
}
```

## Deployment

- Backend: Docker container for Flask application
- Frontend: Vercel or Netlify for Next.js application
- Database: SQLite file for development, PostgreSQL for production

## Testing Requirements

- Unit tests for game logic
- API endpoint tests
- UI component tests
- End-to-end game flow tests

## Deliverables

1. Source code repositories (separate for frontend and backend)
2. Documentation for API endpoints
3. Setup instructions
4. Sample game content
5. Deployment scripts

## AI Content Generation System

### Core Components

1. **World Framework Definition**
    
    - Base setting and lore documentation
    - Character archetypes and relationships
    - Major plot points and story arcs
    - Thematic elements and tone guidelines
2. **Prompt Engineering System**
    
    - Template creation and management
    - Dynamic variable insertion based on game state
    - Multi-stage prompting for complex narratives
    - Context window management for long-running stories
3. **Content Validation and Processing**
    
    - Appropriateness filtering
    - Coherence checking against existing narrative
    - Format parsing for different content types
    - Quality assessment metrics
4. **Caching and Persistence**
    
    - Storage of generated content
    - Indexing for efficient retrieval
    - Versioning to track narrative evolution
    - Session-specific content management
5. **Narrative Memory System**
    
    - Tracking of key player decisions
    - Character relationship states
    - Important discovered information
    - Player personality/play style profiling

### Implementation Approach

- Start with hybrid approach (pre-written key scenes with AI-generated details)
- Implement feedback mechanism to rate generated content
- Use AI generation primarily for:
    - Environmental descriptions
    - NPC dialogue variations
    - Side quests and optional content
    - Personalized narrative elements based on player choices

### Guardrails and Fallbacks

- Content moderation to prevent inappropriate narratives
- Pre-written fallback content for all critical story nodes
- Consistency checking to prevent contradictions
- Manual review option for key narrative junctures

## Future Enhancement Possibilities

- User accounts for saving progress across devices
- Multiple story paths/adventures
- Rich text formatting in game descriptions
- Simple illustrations for key scenes
- Ambient sound effects
- Achievement system
- AI-generated visual elements
- Voice narration of AI-generated text
- Player-specific narrative adaptation based on play patterns