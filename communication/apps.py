from abc import ABC, abstractmethod

class Communication(ABC):

    def __init__(self, recipient, message):
        self.recipient = recipient
        self.message = message

    @abstractmethod
    def send_message(self):
        pass
