from difflib import get_close_matches

# Base Command class using the command pattern
class Command:
    def execute(self):
        raise NotImplementedError("Subclasses should implement the execute method.")

# Concrete command for moving in a direction
class MoveCommand(Command):
    def __init__(self, direction):
        self.direction = direction

    def execute(self):
        return f"Moving {self.direction}"

# Factory function for creating move commands
def create_move_command(direction):
    return MoveCommand(direction)

# Mapping of command strings (including abbreviations) to command factory lambdas
COMMAND_MAPPINGS = {
    'north': lambda: create_move_command('north'),
    'n': lambda: create_move_command('north'),
    'south': lambda: create_move_command('south'),
    's': lambda: create_move_command('south'),
    'east': lambda: create_move_command('east'),
    'e': lambda: create_move_command('east'),
    'west': lambda: create_move_command('west'),
    'w': lambda: create_move_command('west')
}

def parse_command(input_command):
    """
    Parses a natural language command, supports abbreviations and fuzzy matching.
    
    :param input_command: String input from the player.
    :return: A Command object or None if the command is not recognized.
    """
    normalized = input_command.lower().strip()
    
    # Check for exact match first
    if normalized in COMMAND_MAPPINGS:
        return COMMAND_MAPPINGS[normalized]()
    
    # Use fuzzy matching if no exact match is found
    possible_matches = get_close_matches(normalized, COMMAND_MAPPINGS.keys(), n=1, cutoff=0.7)
    if possible_matches:
        return COMMAND_MAPPINGS[possible_matches[0]]()
    
    # If no match is found, return None or handle as needed
    return None
