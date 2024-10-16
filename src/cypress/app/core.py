from pathlib import Path

from qtpy import QtWidgets, QtCore
from qtpy.QtWidgets import QWidget, QSplitter

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget,
)

from cypress.app.utils import build_demo_graph, make_jupyter_widget_with_kernel

from cypress.app.nodes import *


class CollapsibleWidget(QtWidgets.QWidget):
    def __init__(self, content_widget, title="Collapsible Widget"):
        super().__init__()
        self.content_widget = content_widget
        self.toggle_button = QtWidgets.QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_content)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)
        self.setLayout(layout)

    def toggle_content(self):
        self.content_widget.setVisible(self.toggle_button.isChecked())


class CypressWindow(QtWidgets.QMainWindow):
    """Main application class."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Cypress")

        self.graph = NodeGraph()
        self.console_widget = make_jupyter_widget_with_kernel()
        self.graph.kernel_manager = self.console_widget.kernel_manager
        self.graph.kernel_client = self.console_widget.kernel_client

        self.propbins_widget = PropertiesBinWidget(parent=None, node_graph=self.graph)

        # Create main splitter
        main_splitter = QSplitter(QtCore.Qt.Horizontal)

        # Add graph widget to the left side of the splitter
        main_splitter.addWidget(self.graph.widget)

        # Create right side widget
        right_widget = QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible console widget
        collapsible_console = CollapsibleWidget(self.console_widget, "Console")
        right_layout.addWidget(collapsible_console)

        # Add properties widget
        right_layout.addWidget(self.propbins_widget)

        # Add right widget to the main splitter
        main_splitter.addWidget(right_widget)

        # Set initial sizes (adjust as needed)
        main_splitter.setSizes([600, 400])

        self.setCentralWidget(main_splitter)

    def setup(self):
        self.graph.set_context_menu_from_file(
            str(Path(__file__).parent / "hotkeys" / "hotkeys.json")
        )

        self.graph.register_nodes(
            [
                ScriptNode,
                SimpleOutputNode,
                ImageNode,
                QConsoleNode,  # TODO: Broken, for some reason can't get an ioloop_thread from within NodeGraph.
            ]
        )

        build_demo_graph(self.graph)

        def display_properties_bin(node):
            # This function is now redundant as the properties bin is always visible
            # but we'll keep it for potential future use
            pass

        def on_node_created(node):
            if hasattr(node, "on_node_created"):
                node.on_node_created()

        self.graph.node_double_clicked.connect(display_properties_bin)
        self.graph.node_created.connect(on_node_created)

        return self

    def quit(self):
        self.console_widget.kernel_client.stop_channels()
        self.console_widget.kernel_manager.shutdown_kernel()

        print("Shutdown complete, Goodbye.")
