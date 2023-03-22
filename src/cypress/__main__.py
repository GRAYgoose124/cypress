import logging
import signal

from .app.core import App


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = App().setup()
    app.run()


# Deprecated. Kept for compatibility with pre-PEP 621 entry.
if __name__ == "__main__":
    main()