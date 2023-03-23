from pathlib import Path

from qtpy import QtWidgets, QtCore
from qtpy.QtWidgets import QWidget

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget
)

from cypress.app.utils import build_demo_graph
from cypress.app.consolewidget import make_jupyter_widget_with_kernel


from .nodes import ScriptNode, SimpleOutputNode


class CypressWindow(QtWidgets.QMainWindow):
    """ Main application class. """

    def __init__(self) -> None:
        super().__init__()
        self.title = "Cypress"

        self.graph = NodeGraph()
        self.console = make_jupyter_widget_with_kernel()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graph.widget)
        layout.addWidget(self.console)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setup(self):
        self.graph.set_context_menu_from_file(
            Path(__file__).parent / 'hotkeys/hotkeys.json')

        self.graph.register_nodes([
            ScriptNode,
            SimpleOutputNode
        ])

        properties_bin = PropertiesBinWidget(node_graph=self.graph)
        properties_bin.setWindowFlags(QtCore.Qt.Tool)

        def display_properties_bin(node):
            if not properties_bin.isVisible():
                properties_bin.show()

        self.graph.node_double_clicked.connect(display_properties_bin)

        build_demo_graph(self.graph)   

        return self
