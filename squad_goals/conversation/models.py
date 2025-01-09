from typing import List, Optional, Dict

from pydantic import BaseModel


class Message(BaseModel):
    content: str
    source: str
    role: Optional[str] = None
    to: Optional[str] = None
    date: Optional[str] = None

    def __str__(self):
        if self.date:
            return f"{self.date} {self.source}: {self.content}"
        return f"{self.source}: {self.content}"


class Conversation(BaseModel):
    messages: Optional[List[Message]] = []
    verbose: bool = False

    def __str__(self):
        to_return = f"Conversation with {len(self.messages)} messages:\n"
        for message in self.messages:
            to_return += f"{message}\n"

        return to_return

    def messages_as_dicts(self) -> List[Dict[str, str]]:
        return [{'role': message.role, 'content': message.content} for message in self.messages]

    def __len__(self):
        return len(self.messages)

# Is the conersation agent an agent with a converation and on every new agent, it just does it to add the resulting message to the chat?
