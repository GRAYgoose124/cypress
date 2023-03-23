import logging
import random
import time
import traceback

from Qt import QtWidgets
from Qt.QtGui import QColor

from NodeGraphQt import BaseNode, NodeBaseWidget
from NodeGraphQt.constants import NodePropWidgetEnum


logger = logging.getLogger(__name__)


def flatten(l):
    f = []
    for sl in l:
        f.extend(sl)

    return f


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

    SCRIPT_OUTVAR = 'Final'

    def __init__(self):
        super(ScriptNode, self).__init__()
        self.add_input('In', multi_input=True)
        self.add_output('Out')

        self.create_property('Execution.Results', value=None,
                             tab='Execution', widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property('Execution.Locals', value=None, 
                                tab='Execution', widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property('Execution.Context', value=None,
                             tab='Execution', widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property('Execution.ID', value=None, tab='Execution',
                             widget_type=NodePropWidgetEnum.QLABEL.value)
        self.create_property('Execution.State', None, tab='Execution', widget_type=NodePropWidgetEnum.QLINE_EDIT.value)

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
        nodes = [n[1] for n in filter(lambda x: x[0].name() == 'In', items)]
        return flatten(nodes)

    @property
    def code_outputs(self):
        """ Get all output nodes. """
        items = self.connected_output_nodes().items()
        nodes = [n[1] for n in filter(lambda x: x[0].name() == 'Out', items)]
        return flatten(nodes)

    def execute(self):
        """ Execute the script. """
        context = self.execute_tree()
        del context['__builtins__']

        results = context[ScriptNode.SCRIPT_OUTVAR]

        self.set_property('Execution.Results', results)
        self.set_property('Execution.Context', context)

    # executable
    def _exe_func(self, context):
        """ Execution wrapper for this node. """
        if self.code is None:
            return context

        code = self.code

        already_exist = list(context.keys())
        try:
            exec(code, context)

            self._locals = {k: context[k] for k in context.keys() if k not in already_exist and k != '__builtins__'}
            self.set_property('Execution.Locals', self._locals)
            self.set_property('Execution.State', 'Success')
        except Exception as e:
            e_msg = f"Error on {self.name()}"
            logger.error(e_msg)
            traceback.print_exc()
            self.set_property('Execution.State', f"Error: {e}")
        finally:
            self.set_property('Execution.ID', context['__execution_id'])

        return context

    def execute_tree(self, ctx=None):
        """ Execute the tree rooted at this node with a unified context. """
        if ctx is not None:
            context = ctx
        else:
            exe_id = f"{time.time_ns()}x{random.randint(0, 1000000)}"
            context = {ScriptNode.SCRIPT_OUTVAR: None, '__execution_id': exe_id}

        for node in self.code_inputs:
            node.execute_tree(ctx=context)

        self._exe_func(context)

        return context
