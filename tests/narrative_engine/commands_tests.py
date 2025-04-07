# filepath: /home/ianphil/src/text_adventure/tests/narrative_engine/commands_tests.py
import pytest
from narrative_engine.commands import Command, MoveCommand, create_move_command, parse_command, COMMAND_MAPPINGS

class TestCommand:
    def test_base_command(self):
        # Base Command should raise NotImplementedError when execute is called
        command = Command()
        with pytest.raises(NotImplementedError):
            command.execute()

class TestMoveCommand:
    def test_move_command_initialization(self):
        # Test initialization with different directions
        north_command = MoveCommand("north")
        assert north_command.direction == "north"
        
        south_command = MoveCommand("south")
        assert south_command.direction == "south"
    
    def test_move_command_execute(self):
        # Test execute method returns correct string
        north_command = MoveCommand("north")
        assert north_command.execute() == "Moving north"
        
        east_command = MoveCommand("east")
        assert east_command.execute() == "Moving east"

class TestCommandFactory:
    def test_create_move_command(self):
        # Test if the factory creates proper MoveCommand objects
        command = create_move_command("north")
        assert isinstance(command, MoveCommand)
        assert command.direction == "north"
        assert command.execute() == "Moving north"

class TestCommandParser:
    def test_exact_match_commands(self):
        # Test parsing commands with exact matches
        north_command = parse_command("north")
        assert isinstance(north_command, MoveCommand)
        assert north_command.direction == "north"
        
        # Test abbreviations
        n_command = parse_command("n")
        assert isinstance(n_command, MoveCommand)
        assert n_command.direction == "north"
    
    def test_case_insensitive_commands(self):
        # Test case insensitivity
        north_command = parse_command("NORTH")
        assert isinstance(north_command, MoveCommand)
        assert north_command.direction == "north"
        
        south_command = parse_command("South")
        assert isinstance(south_command, MoveCommand)
        assert south_command.direction == "south"
    
    def test_whitespace_handling(self):
        # Test handling whitespace
        command = parse_command("  east  ")
        assert isinstance(command, MoveCommand)
        assert command.direction == "east"
    
    def test_fuzzy_matching(self):
        # Test fuzzy matching for similar commands
        command = parse_command("noth")  # typo for "north"
        assert isinstance(command, MoveCommand)
        assert command.direction == "north"
    
    def test_unknown_command(self):
        # Test handling of unknown commands
        command = parse_command("jump")
        assert command is None