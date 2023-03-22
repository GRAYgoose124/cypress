from Qt import QtWidgets

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

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._text_edit)


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

        self.add_custom_widget(NodeTextAreaWidget(self.view), tab="Custom")

    