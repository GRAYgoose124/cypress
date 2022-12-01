from abc import ABCMeta, abstractmethod

# TODO: while a meta makes sense, the actual necessitation of it does not.
# Since DPG isn't object oriented, this doesn't constrain the user in a
# way that makes a metaclass add any true safety.
class NodeABC(metaclass=ABCMeta):
    name = ""
    tags = ""