from pathlib import Path

from Qt import QtWidgets, QtCore

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget
)

from cypress.app.utils import build_demo_graph


from .nodes import ScriptNode, SimpleOutputNode


class App(QtWidgets.QApplication):
    """ Main application class. """

    def __init__(self) -> None:
        self.title = "Cypress"
        self.size = (1280, 720)

        self.graph = None

        super().__init__([])

    def setup(self):
        graph = NodeGraph()
        self.graph = graph

        graph.set_context_menu_from_file(
            Path(__file__).parent / 'hotkeys/hotkeys.json')

        graph.register_nodes([
            ScriptNode,
            SimpleOutputNode
        ])

        # create a node properties bin widget.
        properties_bin = PropertiesBinWidget(node_graph=graph)
        properties_bin.setWindowFlags(QtCore.Qt.Tool)

        def display_properties_bin(node):
            if not properties_bin.isVisible():
                properties_bin.show()

        # wire function to "node_double_clicked" signal.
        graph.node_double_clicked.connect(display_properties_bin)

        graph.widget.resize(*self.size)
        graph.widget.show()

        build_demo_graph(graph)   

        return self

    def run(self, setup=False):
        if setup:
            self.setup()

        self.exec_()
