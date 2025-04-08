# filepath: /home/ianphil/src/text_adventure/tests/narrative_engine/narrative_memory_tests.py
import pytest
from narrative_engine.narrative_memory import NarrativeMemory

class TestNarrativeMemory:
    def test_init(self):
        """Test initialization of NarrativeMemory class."""
        memory = NarrativeMemory()
        assert memory.events == []
    
    def test_add_event(self):
        """Test adding events to narrative memory."""
        memory = NarrativeMemory()
        memory.add_event("Player entered the cave")
        assert memory.events == ["Player entered the cave"]
        
        memory.add_event("Player found a key")
        assert len(memory.events) == 2
        assert memory.events == ["Player entered the cave", "Player found a key"]
    
    def test_get_log_with_events(self):
        """Test retrieving log with events."""
        memory = NarrativeMemory()
        memory.add_event("Player entered the cave")
        memory.add_event("Player found a key")
        
        expected_log = "Previous events:\nPlayer entered the cave\nPlayer found a key\n"
        assert memory.get_log() == expected_log
    
    def test_get_log_no_events(self):
        """Test retrieving log without any events."""
        memory = NarrativeMemory()
        assert memory.get_log() == ""
    
    def test_clear(self):
        """Test clearing narrative memory."""
        memory = NarrativeMemory()
        memory.add_event("Player entered the cave")
        memory.add_event("Player found a key")
        
        assert len(memory.events) == 2
        
        memory.clear()
        assert memory.events == []
        assert memory.get_log() == ""