# Cypress

Cypress is a simple node-based Python editor.

![](https://raw.githubusercontent.com/GRAYgoose124/cypress/main/screenshots/cypress_1.png)

It utilizes [NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt) for the node editor, and `Qt.py` for Qt bindings. 

## Installation
    > poetry install

with pyside2:
    > poetry install [-E pyside2]

On windows you may need to install the latest graphviz and install pygraphviz with something akin to:

    pip install --global-option=build_ext --global-option="-IC:\Program Files\Graphviz\include" --global-option="-LC:\Program Files\Graphviz\lib" pygraphviz

[Qt.py](https://github.com/mottosso/Qt.py) is a wrapper for common Qt backends, please make sure you install one yourself. Cypress was developed with PySide2 and it can be installed by including the extras `pyside2`.

### Run
    > cypress

![](https://raw.githubusercontent.com/GRAYgoose124/cypress/main/screenshots/cypress_2.png)
