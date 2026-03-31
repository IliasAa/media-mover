from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from screens.observer import Observer


class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer: "Observer") -> None:
        """
        Attach an observer to the subject.
        """

    @abstractmethod
    def detach(self, observer: "Observer") -> None:
        """
        Detach an observer from the subject.
        """

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
