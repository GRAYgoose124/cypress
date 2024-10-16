from qtconsole.rich_jupyter_widget import RichJupyterWidget
from NodeGraphQt import BaseNode, NodeBaseWidget


class QConsoleNodeWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(QConsoleNodeWidget, self).__init__(parent, name="QConsole")
        self.cwidget = RichJupyterWidget()
        self.set_custom_widget(self.cwidget)

    def set_value(self, value):
        pass

    def get_value(self):
        pass


class QConsoleNode(BaseNode):
    __identifier__ = "cypress.nodes"

    NODE_NAME = "QConsole"

    def __init__(self):
        super(QConsoleNode, self).__init__()

        self.add_input("in")

        self.console_widget = QConsoleNodeWidget(self.view)
        self.add_custom_widget(self.console_widget)

    def start_console(self):
        w = self.console_widget.cwidget
        w.kernel_manager = self.graph.kernel_manager
        w.kernel_client = self.graph.kernel_manager.client()
        w.kernel_client.start_channels()

    # custom connection made in core.py
    def on_node_created(self):
        self.start_console()
