import logging
import signal

from qtpy.QtWidgets import QApplication
from cypress.app.core import CypressWindow


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("traitlets").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication([])

    window = CypressWindow().setup()
    window.show()

    app.exec_()

    window.quit()



# Deprecated. Kept for compatibility with pre-PEP 621 entry.
if __name__ == "__main__":
    main()
