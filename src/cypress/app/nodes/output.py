from qtpy import QtWidgets
from qtpy.QtGui import QColor, QPalette, QFont
from qtpy.QtCore import Signal, Slot, Qt
from NodeGraphQt import BaseNode, NodeBaseWidget

from cypress.app.nodes.script import ScriptNode


class SimpleOutputWidget(QtWidgets.QWidget):
    """ Simple output widget. """
    def __init__(self, parent=None):
        super(SimpleOutputWidget, self).__init__(parent)

        palette = QPalette()
        font = QFont()
        font.setPointSize(20)
        palette.setColor(palette.Foreground, QColor(255, 255, 255))
        self._result_label = QtWidgets.QLabel(f"", self, palette=palette, font=font)

        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._result_label)


class NodeSimpleOutputWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeSimpleOutputWidget, self).__init__(parent, name='Result')
        self.set_custom_widget(SimpleOutputWidget())
        self.cwidget = self.get_custom_widget()

    def set_value(self, value):
        self.cwidget._result_label.setText(value)

    def get_value(self):
        return self.cwidget._result_label.text()
    

class SimpleOutputNode(BaseNode):
    __identifier__ = 'cypress.nodes.SimpleOutputNode'

    NODE_NAME = 'SimpleOutput'

    CHAINED_PORT_IN = ScriptNode.CHAINED_PORT_IN

    def __init__(self):
        super(SimpleOutputNode, self).__init__()
        self.add_input(self.CHAINED_PORT_IN)

        self._node_widget = NodeSimpleOutputWidget(self.view)
        self.add_custom_widget(self._node_widget)

        self.watched_node = None

    def on_input_connected(self, in_port, out_port):
        self.watched_node = out_port.node()

        self.watched_node.output_updated.connect(self.on_results_changed)

    @Slot(object)
    def on_results_changed(self, results):
        self._node_widget.set_value(str(results))

