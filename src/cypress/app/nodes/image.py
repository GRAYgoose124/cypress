import codecs
import pickle

from NodeGraphQt import BaseNode, NodeBaseWidget
from NodeGraphQt.constants import NodePropWidgetEnum

from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Slot
from qtpy.QtGui import QImage

from cypress.app.nodes.script import ScriptNode


class ImageGraphicsWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent=None, image=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setMinimumSize(200, 200)

        self.image = image
    
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
    def internal_image(self):
        return self._image
    
    @internal_image.setter
    def internal_image(self, image):
        self._image = image
        self.graphics_widget.update_image(image)


class NodeImageWidget(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NodeImageWidget, self).__init__(parent, name='Image')
        self.set_custom_widget(ImageWidget())
        self.cwidget = self.get_custom_widget()

        self.image_array = None

    def set_value(self, value: bytes | str):
        if value is None:
            return
        elif isinstance(value, bytes):
            self.image_array = value
        elif isinstance(value, str):
            # value is a string-encoded bytes object, so we need to decode it
            self.image_array = codecs.decode(value.encode('utf-8'), 'base64')
        else:
            raise ValueError('value must be bytes or str-encoded bytes, not {}'.format(type(value)))
        
        image = QImage.fromData(self.image_array)
        self.cwidget.internal_image = image
        self.cwidget.update()

    def get_value(self):
        if self.image_array is None:
            return None
        
        # self.image_array is a bytes object, so we need to encode it to a string
        return codecs.encode(self.image_array, 'base64').decode('utf-8')
        # return self.cwidget.internal_image    # not serializable - exchange with path and load?
    

class ImageNode(BaseNode):
    __identifier__ = 'cypress.nodes'
    NODE_NAME = 'Image'

    CHAINED_PORT_IN = ScriptNode.CHAINED_PORT_IN

    def __init__(self):
        super(ImageNode, self).__init__()
        self.add_input(self.CHAINED_PORT_IN)

        self.source_node = None

        self.image_widget = NodeImageWidget(self.view)
        self.add_custom_widget(self.image_widget)

    @Slot(bytes)
    def update_image(self, image):
        self.image_widget.set_value(image)

    # TODO: can probably generalize the below methods to a ChainNode
    def set_source_node(self, node):
        self.unset_source_node()
        
        self.source_node = node
        self.source_node.image_update.connect(self.update_image)

    def unset_source_node(self):
        if self.source_node is None:
            return
        
        self.source_node.image_update.disconnect(self.update_image)
        self.source_node = None

    def on_input_connected(self, in_port, out_port):
        self.set_source_node(out_port.node())

    def on_input_disconnected(self, in_port, out_port):
        self.unset_source_node()



