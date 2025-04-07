import pytest
from narrative_engine.graph import Node, NarrativeGraph

@pytest.fixture
def basic_node():
    return Node("room1", "A dark room")

@pytest.fixture
def complex_node():
    return Node(
        "room2", 
        "A bright room",
        exits={"north": "room1"},
        items=["key"],
        actions={"examine": "You see a window"}
    )

@pytest.fixture
def narrative_graph():
    graph = NarrativeGraph()
    room1 = Node("room1", "First room")
    room2 = Node("room2", "Second room")
    return graph, room1, room2

class TestNode:
    def test_node_initialization(self, basic_node):
        assert basic_node.node_id == "room1"
        assert basic_node.description == "A dark room"
        assert basic_node.exits == {}
        assert basic_node.items == []
        assert basic_node.actions == {}

    def test_node_initialization_with_parameters(self, complex_node):
        assert complex_node.exits == {"north": "room1"}
        assert complex_node.items == ["key"]
        assert complex_node.actions == {"examine": "You see a window"}

    def test_node_update(self, basic_node):
        basic_node.update(
            description="An updated room",
            exits={"south": "room2"},
            items=["sword"],
            actions={"look": "You see a door"}
        )
        assert basic_node.description == "An updated room"
        assert basic_node.exits == {"south": "room2"}
        assert basic_node.items == ["sword"]
        assert basic_node.actions == {"look": "You see a door"}

class TestNarrativeGraph:
    def test_add_node(self, narrative_graph):
        graph, room1, _ = narrative_graph
        graph.add_node(room1)
        assert "room1" in graph.nodes
        assert graph.nodes["room1"].description == "First room"

    def test_add_duplicate_node(self, narrative_graph):
        graph, room1, _ = narrative_graph
        graph.add_node(room1)
        with pytest.raises(ValueError):
            graph.add_node(room1)

    def test_remove_node(self, narrative_graph):
        graph, room1, room2 = narrative_graph
        graph.add_node(room1)
        graph.add_node(room2)
        graph.add_transition("room1", "north", "room2")
        
        graph.remove_node("room2")
        assert "room2" not in graph.nodes
        assert "north" not in graph.nodes["room1"].exits

    def test_remove_nonexistent_node(self, narrative_graph):
        graph, _, _ = narrative_graph
        with pytest.raises(ValueError):
            graph.remove_node("nonexistent")

    def test_update_node(self, narrative_graph):
        graph, room1, _ = narrative_graph
        graph.add_node(room1)
        graph.update_node("room1", description="Updated room")
        assert graph.nodes["room1"].description == "Updated room"

    def test_add_transition(self, narrative_graph):
        graph, room1, room2 = narrative_graph
        graph.add_node(room1)
        graph.add_node(room2)
        graph.add_transition("room1", "north", "room2")
        assert graph.nodes["room1"].exits["north"] == "room2"

    def test_add_invalid_transition(self, narrative_graph):
        graph, room1, _ = narrative_graph
        graph.add_node(room1)
        with pytest.raises(ValueError):
            graph.add_transition("room1", "north", "nonexistent")