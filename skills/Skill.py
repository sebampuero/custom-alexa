from abc import ABC, abstractmethod
import typing

class Skill(ABC):

    def __init__(self, name: str) -> None:
        self.__name = name

    @abstractmethod
    def trigger(self, transcript: str) -> typing.Tuple[bool, str]:
        """
        Execute this skill's task based on transcript passed. If transcript does not match this skill, return the original transcript and False
        """
        pass

    def __str__(self) -> str:
        return self.__name

