# narrative_engine/narrative_memory.py

class NarrativeMemory:
    def __init__(self):
        self.events = []

    def add_event(self, event):
        """
        Add a narrative event to the memory log.
        
        :param event: A narrative event as a string.
        """
        self.events.append(event)

    def get_log(self):
        """
        Return the entire narrative memory log as a single string.
        The log is prefixed with a header to indicate context.
        
        :return: A string combining all previous narrative events.
        """
        if self.events:
            return "Previous events:\n" + "\n".join(self.events) + "\n"
        return ""
    
    def clear(self):
        """
        Clear the narrative memory log.
        """
        self.events = []
