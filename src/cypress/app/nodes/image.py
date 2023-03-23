from NodeGraphQt import BaseNode, NodeBaseWidget
from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Slot


class ImageWidget(QtWidgets.QWidget):
    """ A simple widget that displays an image. """
    def __init__(self, image=None, parent=None):
        super().__init__(parent)
        self.image = image

    def paintEvent(self, event):
        if self.image is None:
            return
        
        painter = QtGui.QPainter(self)
        painter.drawImage(self.rect(), self.image)

    def sizeHint(self):
        if self.image is None:
            return QtCore.QSize(0, 0)
        
        return self.image.size()
    

class NodeImageWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeImageWidget, self).__init__(parent, name='Image')
        self.set_custom_widget(ImageWidget())
        self.cwidget = self.get_custom_widget()

    def set_value(self, image):
        self.cwidget.image = image

    def get_value(self):
        return self.cwidget.image
    

class ImageNode(BaseNode):
    __identifier__ = 'cypress.nodes'
    NODE_NAME = 'Image'

    def __init__(self):
        super(ImageNode, self).__init__()
        self.add_input('in')

        self.image_widget = NodeImageWidget(self.view)
        self.add_custom_widget(self.image_widget)

    @Slot(QtGui.QImage)
    def update_image(self, image):
        self.image_widget.set_value(image)

    def on_input_connected(self, in_port, out_port):
        out_port.node().image_updated.connect(self.update_image)

