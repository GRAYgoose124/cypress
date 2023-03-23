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


from .nodes import *


class CypressWindow(QtWidgets.QMainWindow):
    """ Main application class. """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Cypress')

        self.graph = NodeGraph()
        self.console_widget = make_jupyter_widget_with_kernel()
        self.graph.kernel_manager = self.console_widget.kernel_manager
        self.graph.kernel_client = self.console_widget.kernel_client

        self.console_widget.setWindowFlags(QtCore.Qt.Tool)

        self.propbins_widget = PropertiesBinWidget(node_graph=self.graph)
        self.propbins_widget.setWindowFlags(QtCore.Qt.Tool)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        tab_widget = QtWidgets.QTabWidget()
        tab_widget.addTab(self.console_widget, 'Console')
        tab_widget.addTab(PropertiesBinWidget(node_graph=self.graph), 'Properties')

        layout.addWidget(self.graph.widget)
        layout.addWidget(tab_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setup(self):
        self.graph.set_context_menu_from_file(
            Path(__file__).parent / 'hotkeys/hotkeys.json')

        self.graph.register_nodes([
            ScriptNode,
            SimpleOutputNode,
            ImageNode
            #QConsoleNode   # TODO: Broken, for some reason can't get an ioloop_thread from within NodeGraph.
        ])

        build_demo_graph(self.graph)   
   
        def display_properties_bin(node):
            if not self.propbins_widget.isVisible():
                self.propbins_widget.show()
                self.propbins_widget.raise_()

        self.graph.node_double_clicked.connect(display_properties_bin)

        return self

    def quit(self):
        self.console_widget.kernel_client.stop_channels()
        self.console_widget.kernel_manager.shutdown_kernel()