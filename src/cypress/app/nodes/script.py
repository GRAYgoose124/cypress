import codecs
import logging
import random
import time
import traceback

from Qt import QtWidgets
from Qt.QtGui import QColor
from Qt.QtCore import Signal, Slot, QObject

from NodeGraphQt import BaseNode, NodeBaseWidget
from NodeGraphQt.constants import NodePropWidgetEnum


logger = logging.getLogger(__name__)


class ScriptNodeExecutionError(Exception):
    pass


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
        super(NodeTextAreaWidget, self).__init__(parent, name='Code Area')
        self.set_custom_widget(TextAreaWidget())
        self.cwidget = self.get_custom_widget()

    def set_value(self, value):
        self.cwidget._text_edit.setText(value)

    def get_value(self):
        return self.cwidget._text_edit.toPlainText()


class ScriptNode(QObject, BaseNode):
    """ Executable script node. 
    
        ScriptNodes with 'In' -> 'Out' connections will be executed 
        with a unified context.
    """
    __identifier__ = 'cypress.nodes.ScriptNode'
    NODE_NAME = 'Script'

    CHAINED_PORT_IN = 'In'
    CHAINED_PORT_OUT = 'Out'
    
    SCRIPT_OUTVAR = 'Final'

    output_updated = Signal(object)

    def __init__(self):
        QObject.__init__(self)
        BaseNode.__init__(self)

        self.add_input(ScriptNode.CHAINED_PORT_IN, multi_input=True)
        self.add_output(ScriptNode.CHAINED_PORT_OUT)

        self.create_property('State', None, 
                        tab='Execution', widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property('ID', value=None, 
                             tab='Execution', widget_type=NodePropWidgetEnum.QLABEL.value)
        self.create_property('Results', value=None,
                             tab='Execution', widget_type=NodePropWidgetEnum.QLINE_EDIT.value)
        self.create_property('Locals', value=None, 
                                tab='Execution', widget_type=NodePropWidgetEnum.QTEXT_EDIT.value)
        self.create_property('Context', value=None,
                             tab='Execution', widget_type=NodePropWidgetEnum.QTEXT_EDIT.value)

        self._last_executed = None

        self._text_widget = NodeTextAreaWidget(self.view)
        self.add_custom_widget(self._text_widget)

        self._text_widget.cwidget.exe_button.clicked.connect(self.execute)

        #self.output_updated = 

    @property
    def code(self):
        """ Get the script code. """
        code = self._text_widget.get_value()
        return code

    @code.setter
    def code(self, value):
        """ Set the script code. """
        self._text_widget.set_value(value)

    @property
    def code_inputs(self):
        """ Get all input nodes. """
        return self.connected_input_nodes()[self.inputs()[ScriptNode.CHAINED_PORT_IN]]

    @property
    def code_outputs(self):
        """ Get all output nodes. """
        return self.connected_output_nodes()[self.outputs()[ScriptNode.CHAINED_PORT_OUT]]

    def execute(self):
        """ Execute the script. """
        try:
            context = self.execute_tree()
        except ScriptNodeExecutionError as e:
            logger.error(e.args[0])
            return
        
        # Only update executed node's Results and Context properties.
        del context['__builtins__']
        results = context[ScriptNode.SCRIPT_OUTVAR]

        self.output_updated.emit(results)

        self.set_property('Results', results)
        self.set_property('Context', context)

    # executable
    def execute_tree(self, ctx=None):
        """ Execute the tree flowing into this node with a unified context. """
        # If a context is provided, use it. Otherwise, create a new one.
        if ctx is not None:
            context = ctx
        else:
            # Set the execution ID for this tree.
            exe_id = f"{random.randint(0, 1000000)}{str(time.time_ns())[-10:]}".encode('utf-8')
            exe_id = codecs.encode(exe_id, 'base64').decode('utf-8')

            context = {ScriptNode.SCRIPT_OUTVAR: None, '__execution_id': exe_id}

        # Execute all input nodes prior to this node's execution
        for node in self.code_inputs:
            node.execute_tree(ctx=context)

        self.execute_node(context)

        return context

    def execute_node(self, context):
        # Do not execute if there is no code.
        if self.code is None:
            return
        
        # Set up execution state.
        if '__execution_id' not in context:
            self.set_property('ID', "ORPHANED")
        else:
            # Prevent the node from executing multiple times in the same execution cycle.
            if self._last_executed != context['__execution_id']:
                self._last_executed = context['__execution_id']
                self.set_property('ID', context['__execution_id'])
            else:
                return
            
        already_created_vars = list(context.keys())
        prior_results = context.get(ScriptNode.SCRIPT_OUTVAR, None)
        success = None

        # Try to execute this node.
        try:
            exec(self.code, context)
            success = True
        except Exception as e:
            traceback.print_exc()
            success = False

        if success:
            # Locals added to the context at this node.
            locals_added_by_this_node = {k: context[k] for k in context.keys() if k not in already_created_vars and k != '__builtins__'}

            # If the output variable has changed, add it to the locals for this node.
            new_results = context.get(ScriptNode.SCRIPT_OUTVAR, None)
            if prior_results != new_results:
                locals_added_by_this_node[ScriptNode.SCRIPT_OUTVAR] = new_results

            self.set_property('Locals', locals_added_by_this_node)
            self.set_property('State', 'Success')
        else:
            self.set_property('Locals', None)
            self.set_property('State', 'Error')

            raise ScriptNodeExecutionError(f"Error at {self.name()}. See console for details.")