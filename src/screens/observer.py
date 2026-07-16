from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.subject import Subject


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject: "Subject") -> None:
        """
        Receive update from subject.
        """


"""
Concrete Observers react to the updates issued by the Subject they had been
attached to.
"""
