from pathlib import Path
from qtpy import QtWidgets
from qtpy.QtGui import QColor, QPalette, QFont
from qtpy.QtCore import Signal, Slot, Qt
from NodeGraphQt import BaseNode, NodeBaseWidget

from cypress.app.nodes.script import ScriptNode

class SimpleInputWidget(QtWidgets.QWidget):
    """ Simple input widget. """
    def __init__(self, parent=None):
        super(SimpleInputWidget, self).__init__(parent)

        self.selected_invar = None

        self.invar_box = QtWidgets.QLineEdit(self)
        self.invar_box.setPlaceholderText('Input')
        self.invar_box.textChanged.connect(self.set_selected_invar)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.invar_box)

    def set_selected_invar(self, invar):
        self.selected_invar = invar


class NodeSimpleInputWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeSimpleInputWidget, self).__init__(parent, name='Input')
        self.set_custom_widget(SimpleInputWidget())
        self.cwidget = self.get_custom_widget()

    def set_value(self, value):
        self.cwidget.invar_box.setText(value)

    def get_value(self):
        return self.cwidget.invar_box.text()
    

class SimpleInputNode(BaseNode):
    """ Simple input node. """
    __identifier__ = 'cypress.nodes'
    NODE_NAME = 'Input'

    input_update = Signal(object)

    def __init__(self):
        super(SimpleInputNode, self).__init__()
        self.add_output(ScriptNode.CHAINED_PORT_OUT)
        
        self.dest_node: ScriptNode = None
        self.value = None

        self._node_widget = NodeSimpleInputWidget(self.view)
        self.add_custom_widget(self._node_widget)

    def process_shell_msg(self, msg):
        """ Process the shell message. """
        if msg['msg_type'] == 'execute_result':
            self.value = msg['content']['data']['text/plain']
            self.input_update.emit(self.value)
            
    def get_var_from_kernel(self):
        """ Get the variable from the kernel. """
        varname = self._node_widget.get_value() or 'Input'
        self.graph.kernel_client.execute(varname)

        return varname, self.value

    def set_dest_node(self, node):
        self.dest_node = node

    def unset_dest_node(self):
        if self.dest_node is None:
            return
        
    def on_input_connected(self, in_port, out_port):
        """ Called when an input port is connected. """
        self.on_output_connected(out_port, in_port)

    def on_input_disconnected(self, in_port, out_port):
        """ Called when an input port is disconnected. """
        self.on_output_disconnected(out_port, in_port)

    def on_output_connected(self, in_port, out_port):
        """ Called when an output port is connected. """
        self.set_dest_node(in_port.node())

        self.graph.kernel_client.shell_channel.connect(self.process_shell_msg)
        self.input_update.connect(in_port.node().update_input_var)

    def on_output_disconnected(self, in_port, out_port):
        """ Called when an output port is disconnected. """
        self.unset_dest_node()