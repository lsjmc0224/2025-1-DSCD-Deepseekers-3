from abc import ABC, abstractmethod

class Analyzable(ABC):
    @property
    @abstractmethod
    def content(self) -> str:
        pass

    @abstractmethod
    def get_original(self) -> object:
        pass