from llama_index.core.workflow import Event

class GenPromptEvent(Event):
    content: str

class PromptGeneratedEvent(Event):
    content: str

class StreamEvent(Event):
    target: str
    delta: str

class GenImageEvent(Event):
    content: str

class RewriteQueryEvent(Event):
    pass