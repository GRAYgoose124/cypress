import logging
import traceback
from Qt import QtWidgets
from Qt.QtGui import QColor

from NodeGraphQt import BaseNode, BaseNodeCircle, NodeBaseWidget


logger = logging.getLogger(__name__)

class TextAreaWidget(QtWidgets.QWidget):
    """ Text area widget for ScriptNode. """
    def __init__(self, parent=None):
        super(TextAreaWidget, self).__init__(parent)
        self._text_edit = QtWidgets.QTextEdit(self)
        palette = self._text_edit.palette()
        palette.setColor(palette.Base, QColor(0, 0, 0))
        palette.setColor(palette.Text, QColor(255, 255, 255))
        self._text_edit.setPalette(palette)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text_edit)

        self.exe_button = QtWidgets.QPushButton('Execute')
        layout.addWidget(self.exe_button)


class NodeTextAreaWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeTextAreaWidget, self).__init__(parent)
        self.set_custom_widget(TextAreaWidget())
        self.cwidget = self.get_custom_widget()

    def set_value(self, value):
        self.cwidget._text_edit.setText(value)

    def get_value(self):
        return self.cwidget._text_edit.toPlainText()


class ScriptNode(BaseNode):
    """ Executable script node. """
    __identifier__ = 'cypress.nodes.ScriptNode'
    NODE_NAME = 'Script'

    def __init__(self):
        super(ScriptNode, self).__init__()
        self.add_input('In', multi_input=True)
        self.add_output('Out')

        self.execution_id = None
        self.script_output = 'Final'

        self._text_widget = NodeTextAreaWidget(self.view)
        self.add_custom_widget(self._text_widget, tab="Custom")

        self._text_widget.cwidget.exe_button.clicked.connect(self.execute)
           
    @property
    def code(self):
        """ Get the script code. """
        return self._text_widget.get_value()
    
    @code.setter
    def code(self, value):
        """ Set the script code. """
        self._text_widget.set_value(value)
    
    @property
    def code_inputs(self):
        """ Get all input nodes. """
        items = self.connected_input_nodes().items()
        nodes = list(filter(lambda x: x[0].name()[0] == 'In', items ))
        return [n[1] for n in nodes]
    
    @property
    def code_outputs(self):
        """ Get all output nodes. """
        items = self.connected_output_nodes().items()
        nodes = list(filter(lambda x: x[0].name()[0] == 'Out', items ))
        return [n[1] for n in nodes]

    def execute(self):
        """ Execute the script. """
        self.execute_tree()
    
    # executable
    def _exe_func(self, context):
        """ Execution wrapper for this node. """
        if self.code is None:
            return context
            
        try:
            exec(self.code, context)
        except Exception as e:
            logger.info(f"Error on {self.name()} with context: {context[self.script_output]}")
            traceback.print_exc()
        
        return context

    def execute_tree(self, ctx=None):
        """ Execute the tree rooted at this node with a unified context. """
        if ctx is not None:
            context = ctx
        else:
            context = {self.script_output: None}
       
        for node in self.code_inputs:
            node.execute_tree(ctx=context)

        self._exe_func(context)

        return context

    