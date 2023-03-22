from Qt import QtWidgets
from Qt.QtGui import QColor

from NodeGraphQt import BaseNode, BaseNodeCircle, NodeBaseWidget


# def create_script_node(
#     name: str,
#     size: tuple[float, float] = (150, 200),
#     pos: tuple[float, float] = (0, 0),
#     parent = None
# ):
#     with dpg.node(label="Script", pos=pos, parent=parent) as n_id:
#         dpg.add_node_attribute(tag=f"{n_id}.In", attribute_type=dpg.mvNode_Attr_Input)
#         dpg.add_node_attribute(tag=f"{n_id}.Out", attribute_type=dpg.mvNode_Attr_Output)

#         with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
#             dpg.add_input_text(tag=f"{n_id}.Code", multiline=True, width=size[1], height=size[0])
            
#         return n_id


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

        self._text_widget = NodeTextAreaWidget(self.view)
        self.add_custom_widget(self._text_widget, tab="Custom")

        self._text_widget.cwidget.exe_button.clicked.connect(self.execute)
           
    @property
    def code(self):
        """ Get the script code. """
        return self._text_widget.get_value()

    def execute(self):
        """ Execute the script. """
        print(self.code)
        return self._text_widget.get_value()
    
    def execute_chain(self):
        pass

    def get_all_roots(self):
        """ Get all root nodes. """
        roots = []

        connected = self.connected_input_nodes()
        for node in connected:
            if not node.connected_input_nodes():
                yield node
            else:
                for root in node.get_all_roots():
                    yield root

        return roots
    