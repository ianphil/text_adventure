import pytest
from narrative_engine.events import Event, EventHandler, door_condition, door_action
from unittest.mock import MagicMock

class TestEvent:
    def test_event_initialization(self):
        # Create a simple test event
        name = "Test Event"
        condition = lambda state: True
        action = lambda state: state.update({"action_executed": True})
        
        event = Event(name, condition, action)
        
        assert event.name == name
        assert event.condition is condition
        assert event.action is action

    def test_check_and_execute_when_condition_true(self):
        # Create a test event with condition that returns True
        game_state = {"value": 0}
        condition = lambda state: True
        action = lambda state: state.update({"value": state["value"] + 1})
        
        event = Event("Test Event", condition, action)
        result = event.check_and_execute(game_state)
        
        assert result is True
        assert game_state["value"] == 1

    def test_check_and_execute_when_condition_false(self):
        # Create a test event with condition that returns False
        game_state = {"value": 0}
        condition = lambda state: False
        action = lambda state: state.update({"value": state["value"] + 1})
        
        event = Event("Test Event", condition, action)
        result = event.check_and_execute(game_state)
        
        assert result is False
        assert game_state["value"] == 0  # Action should not have executed

class TestEventHandler:
    def test_register_event(self):
        handler = EventHandler()
        event = Event("Test Event", lambda state: True, lambda state: None)
        
        handler.register_event(event)
        
        assert len(handler.events) == 1
        assert handler.events[0] is event

    def test_process_events_none_triggered(self):
        handler = EventHandler()
        game_state = {"test": True}
        
        # Add events with conditions that return False
        handler.register_event(Event("Event 1", lambda state: False, lambda state: None))
        handler.register_event(Event("Event 2", lambda state: False, lambda state: None))
        
        triggered = handler.process_events(game_state)
        
        assert len(triggered) == 0

    def test_process_events_some_triggered(self):
        handler = EventHandler()
        game_state = {"count": 0}
        
        # Add one event that will trigger and one that won't
        handler.register_event(Event("Event 1", lambda state: True, lambda state: state.update({"count": state["count"] + 1})))
        handler.register_event(Event("Event 2", lambda state: False, lambda state: None))
        
        triggered = handler.process_events(game_state)
        
        assert len(triggered) == 1
        assert "Event 1" in triggered
        assert game_state["count"] == 1

    def test_process_events_all_triggered(self):
        handler = EventHandler()
        game_state = {"count": 0}
        
        # Add multiple events that will all trigger
        handler.register_event(Event("Event 1", lambda state: True, lambda state: state.update({"count": state["count"] + 1})))
        handler.register_event(Event("Event 2", lambda state: True, lambda state: state.update({"count": state["count"] + 2})))
        
        triggered = handler.process_events(game_state)
        
        assert len(triggered) == 2
        assert "Event 1" in triggered
        assert "Event 2" in triggered
        assert game_state["count"] == 3  # 1 + 2

class TestDoorEvent:
    def test_door_condition_not_met_wrong_location(self):
        game_state = MagicMock()
        game_state.current_location = "bedroom"
        game_state.inventory = ["key"]
        game_state.door_open = False
        assert not door_condition(game_state)

    def test_door_condition_not_met_no_key(self):
        game_state = MagicMock()
        game_state.current_location = "hallway"
        game_state.inventory = []
        game_state.door_open = False
        assert not door_condition(game_state)

    def test_door_condition_not_met_door_already_open(self):
        game_state = MagicMock()
        game_state.current_location = "hallway"
        game_state.inventory = ["key"]
        game_state.door_open = True
        assert not door_condition(game_state)

    def test_door_condition_met(self):
        game_state = MagicMock()
        game_state.current_location = "hallway"
        game_state.inventory = ["key"]
        game_state.door_open = False
        assert door_condition(game_state)

    def test_door_action(self):
        game_state = MagicMock()
        game_state.current_location = "hallway"
        game_state.inventory = ["key"]
        game_state.flags = {"door_open": False}
        game_state.exits = {}
        game_state.narrative_graph = '{}'
        game_state.narrative_memory = []

        # Mock load_graph_from_json to return an object with .nodes
        import narrative_engine.graph as graph_module
        graph_mock = MagicMock()
        hallway_node = MagicMock()
        hallway_node.exits = {}
        graph_mock.nodes = {"hallway": hallway_node}
        graph_module.load_graph_from_json = MagicMock(return_value=graph_mock)
        graph_module.graph_to_json = MagicMock(return_value='{"nodes": {}}')

        door_action(game_state)

        assert game_state.flags["door_open"] is True
        assert game_state.exits["door"] == "secret_room"