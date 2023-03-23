from qtpy import QtWidgets
from qtpy.QtGui import QColor, QPalette, QFont
from qtpy.QtCore import Signal, Slot, Qt
from NodeGraphQt import BaseNode, NodeBaseWidget

from cypress.app.nodes.script import ScriptNode


class SimpleOutputWidget(QtWidgets.QWidget):
    """ Simple output widget. """
    def __init__(self, parent=None):
        super(SimpleOutputWidget, self).__init__(parent)

        # to jupyter checkbox
        self.checkbox = QtWidgets.QCheckBox("To Jupyter", self)

        palette = QPalette()
        font = QFont()
        font.setPointSize(16)
        palette.setColor(palette.Foreground, QColor(255, 255, 255))
        self._result_label = QtWidgets.QLabel(f"", self, palette=palette, font=font)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._result_label)
        layout.addWidget(self.checkbox)


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

        self._node_widget.cwidget.checkbox.stateChanged.connect(self.allow_send_to_console)

        self.watched_node = None

    def on_input_connected(self, in_port, out_port):
        self.watched_node = out_port.node()

        self.watched_node.execution_update.connect(self.update_output)

    @Slot(object)
    def update_output(self, context):
        self.context = context
        self._node_widget.set_value(str(context[ScriptNode.SCRIPT_OUTVAR]))

    def allow_send_to_console(self, state):
        if state == Qt.Checked:
            self.watched_node.execution_update.connect(self.send_to_console)
        else:
            self.watched_node.execution_update.disconnect(self.send_to_console)

    @Slot(object)
    def send_to_console(self, context):    
        # embed context in jupyter kernel
        self.graph.kernel_client.execute(f"context = {context}")
