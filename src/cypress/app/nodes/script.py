import codecs
from contextlib import redirect_stderr, redirect_stdout
import io
import logging
import random
import time
import traceback
import types
import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np

from qtpy import QtWidgets, QtGui
from qtpy.QtGui import QColor
from qtpy.QtCore import Signal, Slot, QObject

from NodeGraphQt import BaseNode, NodeBaseWidget
from NodeGraphQt.constants import NodePropWidgetEnum


logger = logging.getLogger(__name__)


class ScriptNodeExecutionError(Exception):
    pass


class TextAreaWidget(QtWidgets.QWidget):
    """ Text area widget for ScriptNode. """

    def __init__(self, parent=None):
        super(TextAreaWidget, self).__init__(parent)
        self._text_edit = QtWidgets.QTextEdit(self, acceptRichText=True,
                                                sizeAdjustPolicy=QtWidgets.QAbstractScrollArea.AdjustToContents)

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
    __identifier__ = 'cypress.nodes'
    NODE_NAME = 'Script'

    CHAINED_PORT_IN = 'In'
    CHAINED_PORT_OUT = 'Out'
    
    SCRIPT_OUTVAR = 'Final'
    SCRIPT_OUTIMAGE = 'Image'

    execution_update = Signal(object)
    image_update = Signal(bytes or None)

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
        self.create_property('stdout', value=None,
                             tab='Execution', widget_type=NodePropWidgetEnum.QTEXT_EDIT.value)

        self.input_var = None
        self._last_executed = None

        self._text_widget = NodeTextAreaWidget(self.view)
        self.add_custom_widget(self._text_widget)

        self._text_widget.cwidget.exe_button.clicked.connect(self.execute)

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
            context = self.execute_tree(self.input_var)
        except ScriptNodeExecutionError as e:
            logger.error(e.args[0])
            return
        
        # Only update executed node's Results and Context properties.
        del context['__builtins__']
        # remove all modules 
        keys = []
        for k, v in context.items():
            if isinstance(v, types.ModuleType):
                keys.append(k)

        for k in keys:
            del context[k]
                          
        results = context[ScriptNode.SCRIPT_OUTVAR]

        self.execution_update.emit(context)

        self.set_property('Results', str(results))
        self.set_property('Context', str(context))

    @Slot(object)
    def update_input_var(self, ctx):
        self.input_var = ctx

    # executable
    def execute_tree(self, ctx=None):
        """ Execute the tree flowing into this node with a unified context. """
        # If a context is provided, use it. Otherwise, create a new one.
        if ctx is not None:
            context = ctx
        else:
            context = {}

        # Update context from all SimpleInputNodes.
        for node in self.connected_input_nodes()[self.inputs()[ScriptNode.CHAINED_PORT_IN]]:
            if node.__class__.__name__ == 'SimpleInputNode':
                varname, value = node._node_widget.get_value(), self.input_var
                context[varname] = value

        if '__execution_id' not in context:
            exe_id = f"{random.randint(0, 1000000)}{str(time.time_ns())[-10:]}".encode('utf-8')
            exe_id = codecs.encode(exe_id, 'base64').decode('utf-8')

            context.update({ScriptNode.SCRIPT_OUTVAR: None, '__execution_id': exe_id})

        # Execute all input nodes prior to this node's execution
        for node in self.code_inputs:
            if isinstance(node, ScriptNode):
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
        prior_image = context.get(ScriptNode.SCRIPT_OUTIMAGE, None)
        success = None

        # Try to execute this node.
        try:
            # Capture stdout and stderr.
            with io.StringIO() as buf, redirect_stdout(buf), redirect_stderr(buf):
                exec(self.code, context)
                self.set_property('stdout', buf.getvalue())

            success = True
        except Exception as e:
            traceback.print_exc()
            success = False

        if success:
            # Locals added to the context at this node.
            locals_added_by_this_node = {k: context[k] for k in context.keys() if k not in already_created_vars and k != '__builtins__' and k != 'Image'}

            # If the output variable has changed, add it to the locals for this node.
            new_results = context.get(ScriptNode.SCRIPT_OUTVAR, None)
            if prior_results != new_results:
                locals_added_by_this_node[ScriptNode.SCRIPT_OUTVAR] = new_results

            new_image = context.get(ScriptNode.SCRIPT_OUTIMAGE, None)
            if new_image != prior_image:
                if isinstance(new_image, np.ndarray):
                    self.image_update.emit(new_image)
                # matplotlib figure
                elif isinstance(new_image, matplotlib.figure.Figure):
                    buf = io.BytesIO()
                    new_image.savefig(buf, format='png')
                    buf.seek(0)
                    self.image_update.emit(buf.read())
                else:
                    self.image_update.emit(None)

            self.set_property('Locals', str(locals_added_by_this_node))
            self.set_property('State', 'Success')
        else:
            self.set_property('Locals', None)
            self.set_property('State', 'Error')

            raise ScriptNodeExecutionError(f"Error at {self.name()}. See console for details.")
    