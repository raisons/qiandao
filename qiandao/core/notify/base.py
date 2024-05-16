#!/usr/bin/env python
from abc import abstractmethod, ABC


class Notification(ABC):

    @abstractmethod
    def send(self, *args, **kwargs):
        pass
