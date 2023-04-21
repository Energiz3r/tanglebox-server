from dataclasses import dataclass
from enum import auto, Enum
from typing import List
from datetime import datetime

class SeparatorStyle(Enum):
    """Different separator style."""

    SINGLE = auto()
    TWO = auto()


@dataclass
class Conversation:
    """A class that keeps all conversation history."""

    system: str
    roles: List[str] = ("Human", "Assistant")
    messages: List[List[str]] = ()
    offset: int = 2
    sep_style: SeparatorStyle = SeparatorStyle.SINGLE
    sep: str = "###"
    sep2: str = None
    modelOutputSeparator: str = None
    skip_next: bool = False

    def copy(self):
        return Conversation(
            system=self.system,
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            offset=self.offset,
            sep_style=self.sep_style,
            sep=self.sep,
            sep2=self.sep2,
            modelOutputSeparator=self.modelOutputSeparator,
        )

    def getPromptForModel(self, shouldUseCustomOutputSep = False):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        systemMessage = self.system + "The current date and time is " + dt_string + "."
        if self.sep_style == SeparatorStyle.SINGLE:
            seperator = self.modelOutputSeparator if shouldUseCustomOutputSep else self.sep
            ret = systemMessage + seperator      
            for role, message in self.messages:
                if message:
                    ret += role + ": " + message + seperator
                else:
                    ret += role + ":"
            return ret
        elif self.sep_style == SeparatorStyle.TWO:
            seps = [self.sep, self.sep2]
            seperator  = self.modelOutputSeparator if shouldUseCustomOutputSep else seps[0]
            ret = systemMessage + seperator
            for i, (role, message) in enumerate(self.messages):
                if message:
                    ret += role + ": " + message + seps[i % 2]
                else:
                    ret += role + ":"
            return ret
        else:
            raise ValueError(f"Invalid style: {self.sep_style}")
        
    def getPromptForOutput(self):
        return self.getPromptForModel(bool(not None == self.modelOutputSeparator))

    def append_message(self, role, message):
        self.messages.append([role, message])

    def to_gradio_chatbot(self):
        ret = []
        for i, (role, msg) in enumerate(self.messages[self.offset :]):
            if i % 2 == 0:
                ret.append([msg, None])
            else:
                ret[-1][-1] = msg
        return ret

    def dict(self):
        return {
            "system": self.system,
            "roles": self.roles,
            "messages": self.messages,
            "offset": self.offset,
            "sep": self.sep,
            "sep2": self.sep2,
        }
