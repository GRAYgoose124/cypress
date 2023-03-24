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

        self.selected_outvar = QtWidgets.QLineEdit(self)
        self.selected_outvar.setPlaceholderText(ScriptNode.SCRIPT_OUTVAR)

        self.console_variable = QtWidgets.QLineEdit(self)
        self.console_variable.setPlaceholderText("context")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        sublayouta = QtWidgets.QVBoxLayout()
        sublayouta.setContentsMargins(0, 0, 0, 0)
        sublayouta.addWidget(self._result_label)
        sublayouta.addWidget(self.selected_outvar)

        sublayoutb = QtWidgets.QHBoxLayout()
        sublayoutb.setContentsMargins(0, 0, 0, 0)
        sublayoutb.addWidget(self.checkbox)
        sublayoutb.addWidget(self.console_variable)

        layout.addLayout(sublayouta)
        layout.addLayout(sublayoutb)


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
    __identifier__ = 'cypress.nodes'
    NODE_NAME = 'SimpleOutput'

    CHAINED_PORT_IN = ScriptNode.CHAINED_PORT_IN

    def __init__(self):
        super(SimpleOutputNode, self).__init__()
        self.add_input(self.CHAINED_PORT_IN)

        self._node_widget = NodeSimpleOutputWidget(self.view)
        self.add_custom_widget(self._node_widget)

        self._node_widget.cwidget.checkbox.stateChanged.connect(self.allow_send_to_console)

        self.source_node: ScriptNode = None

        self.outvar = ScriptNode.SCRIPT_OUTVAR
        self._node_widget.cwidget.selected_outvar.textChanged.connect(self.update_outvar)

        self.console_variable = "context"
        self._node_widget.cwidget.console_variable.textChanged.connect(self.update_console_variable)

    def set_source_node(self, node):
        self.source_node = node

        self.source_node.execution_update.connect(self.update_output)

    def unset_source_node(self):
        if self.source_node is None:
            return
        
        self.source_node.execution_update.disconnect(self.update_output)

    def on_input_connected(self, in_port, out_port):
        self.set_source_node(out_port.node())

    def on_input_disconnected(self, in_port, out_port):
        self.unset_source_node()
        
    @Slot(object)
    def update_output(self, context):
        print(self.source_node, context)
        self.context = context
        self._node_widget.set_value(str(context[self.outvar]))

    def allow_send_to_console(self, state):
        watched_node = self.input(0).connected_ports()[0].node()
        if state == Qt.Checked:
            watched_node.execution_update.connect(self.send_to_console)
        else:
            watched_node.execution_update.disconnect(self.send_to_console)

    @Slot(object)
    def send_to_console(self, context):    
        # embed context in jupyter kernel
        import pickle
        pickle_context = pickle.dumps(context)
        kernel_script = f"import pickle\n{self.console_variable} = pickle.loads({pickle_context})\nNone"
        self.graph.kernel_client.execute(kernel_script)

    def get_from_console(self):
        return self.graph.kernel_client.execute(f"{self.console_variable}")

    @Slot(str)
    def update_outvar(self, outvar):
        self.outvar = outvar

    @Slot(str)
    def update_console_variable(self, console_variable):
        self.console_variable = console_variable