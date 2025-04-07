# narrative_engine/graph.py
import json

class Node:
    def __init__(self, node_id, description, exits=None, items=None, actions=None):
        self.node_id = node_id
        self.description = description
        self.exits = exits if exits else {}   # e.g., {'north': 'hallway'}
        self.items = items if items else []     # e.g., ['key', 'map']
        self.actions = actions if actions else {}  # e.g., {'examine room': 'You see carvings on the wall.'}

    def update(self, description=None, exits=None, items=None, actions=None):
        if description is not None:
            self.description = description
        if exits is not None:
            self.exits = exits
        if items is not None:
            self.items = items
        if actions is not None:
            self.actions = actions

class NarrativeGraph:
    def __init__(self):
        self.nodes = {}  # Dictionary to store nodes by node_id

    def add_node(self, node):
        if node.node_id in self.nodes:
            raise ValueError(f"Node '{node.node_id}' already exists.")
        self.nodes[node.node_id] = node

    def remove_node(self, node_id):
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")
        # Remove node and any transitions referencing it
        del self.nodes[node_id]
        for node in self.nodes.values():
            node.exits = {exit_cmd: dest for exit_cmd, dest in node.exits.items() if dest != node_id}

    def update_node(self, node_id, **kwargs):
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' does not exist.")
        self.nodes[node_id].update(**kwargs)

    def add_transition(self, from_node_id, exit_name, to_node_id):
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError("One or both of the nodes do not exist.")
        self.nodes[from_node_id].exits[exit_name] = to_node_id

    def remove_transition(self, from_node_id, exit_name):
        if from_node_id not in self.nodes or exit_name not in self.nodes[from_node_id].exits:
            raise ValueError("Transition does not exist.")
        del self.nodes[from_node_id].exits[exit_name]

def load_graph_from_json(config_str):
    config = json.loads(config_str)
    graph = NarrativeGraph()
    for node_id, data in config.get("nodes", {}).items():
        node = Node(
            node_id=node_id,
            description=data["description"],
            exits=data.get("exits", {}),
            items=data.get("items", []),
            actions=data.get("actions", {})
        )
        graph.add_node(node)
    return graph
