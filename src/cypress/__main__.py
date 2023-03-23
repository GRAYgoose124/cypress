import logging
import signal

from cypress.app.core import App


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("traitlets").setLevel(logging.WARNING)
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = App().setup()
    app.run()


# Deprecated. Kept for compatibility with pre-PEP 621 entry.
if __name__ == "__main__":
    main()
