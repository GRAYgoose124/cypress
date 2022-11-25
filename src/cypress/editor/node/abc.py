from abc import ABCMeta, abstractmethod


class NodeABC(metaclass=ABCMeta):
    name = ""
    tags = ""

    @abstractmethod
    def add_node(self, node):
        pass

    @abstractmethod
    def remove_node(self, node):
        pass
