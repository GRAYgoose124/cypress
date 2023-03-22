from pathlib import Path
from Qt import QtWidgets, QtCore

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget
)

from cypress.app.editor_builder import EditorBuilder



class App(QtWidgets.QApplication):
    """ Main application class. """
    def __init__(self) -> None:  
        self.title = "Cypress"
        self.size = (1280, 720)
        
        self.graph = None

        super().__init__([])
        

    def setup(self):
        self.graph = NodeGraph()

        self.graph.set_context_menu_from_file(Path(__file__).parent / 'hotkeys/hotkeys.json')

        self.graph.widget.resize(*self.size)
        self.graph.widget.show()

        return self


    def run(self):
        self.exec_()
