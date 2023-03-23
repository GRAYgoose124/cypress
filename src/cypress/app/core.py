from pathlib import Path

from Qt import QtWidgets, QtCore

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget
)


from .nodes import ScriptNode


class App(QtWidgets.QApplication):
    """ Main application class. """

    def __init__(self) -> None:
        self.title = "Cypress"
        self.size = (1280, 720)

        self.graph = None

        super().__init__([])

    def __build_demo_graph(self, graph: NodeGraph):
        def create_node(label, pos):
            node = graph.create_node(
                'cypress.nodes.ScriptNode.ScriptNode', name=f'Script Node {label}', pos=pos)
            return node

        s1 = create_node(1, [0, 0])
        s2 = create_node(2, [400, 0])
        s2b = create_node("2B", [400, 200])
        s3 = create_node(3, [800, 0])
        s3b = create_node("3B", [800, 200])

        s1.code = "print('Hello from Script Node 1!')\na=5"
        s2.code = "print('Hello from Script Node 2!')\nb=10"
        s3.code = "print('Hello from Script Node 3!')\nc=a+b\nprint(c)"

        s2b.code = "print('Hello from Script Node 2B!')\nd=20"
        s3b.code = "print('Hello from Script Node 3B!')\nFinal=c+d\nprint(Final)"

        s1.set_output(0, s2.input(0))
        s1.set_output(0, s2b.input(0))

        s2.set_output(0, s3.input(0))
        s2b.set_output(0, s3b.input(0))
        s3.set_output(0, s3b.input(0))

    def setup(self):
        graph = NodeGraph()
        self.graph = graph

        graph.set_context_menu_from_file(
            Path(__file__).parent / 'hotkeys/hotkeys.json')

        graph.register_nodes([
            ScriptNode
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

        self.__build_demo_graph(graph)

        # fit nodes to the viewer.
        graph.clear_selection()
        graph.fit_to_selection()

        return self

    def run(self, setup=False):
        if setup:
            self.setup()

        self.exec_()
