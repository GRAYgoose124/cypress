from pathlib import Path

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import functools as ft
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

from .app import App


def main():
    app = App()
    app.run()


# Deprecated. Kept for compatibility with pre-PEP 621 entry.
if __name__ == "__main__":
    main()