import sys
from qtpy import QtWidgets

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.manager import QtKernelManager

# The ID of an installed kernel, e.g. 'bash' or 'ir'.
USE_KERNEL = 'python3'

def make_jupyter_widget_with_kernel(manager=None):
    """Start a kernel, connect to it, and create a RichJupyterWidget to use it
    """
    if manager is None:
        kernel_manager = QtKernelManager(kernel_name=USE_KERNEL)
        kernel_manager.start_kernel()
    else:
        kernel_manager = manager

    kernel_client = kernel_manager.client()
    kernel_client.start_channels(shell=True)

    jupyter_widget = RichJupyterWidget()
    jupyter_widget.kernel_manager = kernel_manager
    jupyter_widget.kernel_client = kernel_client
    return jupyter_widget

