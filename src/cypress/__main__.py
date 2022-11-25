import logging

from .app import App


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def main():
    app = App()
    app.run()


# Deprecated. Kept for compatibility with pre-PEP 621 entry.
if __name__ == "__main__":
    main()