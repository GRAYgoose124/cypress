from NodeGraphQt import BaseNode, NodeBaseWidget
from NodeGraphQt.constants import NodePropWidgetEnum

from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Slot


class ImageGraphicsWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.image:
            painter = QtGui.QPainter(self.viewport())
            painter.drawImage(self.rect(), self.image)
            painter.end()

    def update_image(self, image):
        self.image = image
        self.update()
         
            
class ImageWidget(QtWidgets.QWidget):
    """ A simple widget that displays an image. """
    def __init__(self, image=None, parent=None):
        super().__init__(parent)
        self._image = image

        self.graphics_widget = ImageGraphicsWidget(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graphics_widget)

    @property 
    def image(self):
        return self._image
    
    @image.setter
    def image(self, image):
        self._image = image
        self.graphics_widget.update_image(image)


class NodeImageWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeImageWidget, self).__init__(parent, name='Image')
        self.set_custom_widget(ImageWidget())
        self.cwidget = self.get_custom_widget()

    def set_value(self, image):
        self.cwidget.image = image
        self.cwidget.update()

    def get_value(self):
        return self.cwidget.image
    

class ImageNode(BaseNode):
    __identifier__ = 'cypress.nodes'
    NODE_NAME = 'Image'

    def __init__(self):
        super(ImageNode, self).__init__()
        self.add_input('in')

        self.create_property('image', None, widget_type=NodePropWidgetEnum.QLINE_EDIT.value)

        self.image_widget = NodeImageWidget(self.view)
        self.add_custom_widget(self.image_widget)

    @Slot(QtGui.QImage)
    def update_image(self, image):
        self.set_property('image', image)
        self.image_widget.set_value(image)

    def on_input_connected(self, in_port, out_port):
        out_port.node().image_update.connect(self.update_image)

