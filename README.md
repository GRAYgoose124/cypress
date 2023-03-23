# Cypress

Cypress is a simple node-based Python editor.

![](https://raw.githubusercontent.com/GRAYgoose124/cypress/main/screenshots/cypress_1.png)

It utilizes [dearpygui](https://github.com/hoffstadt/DearPyGui) for the node editor and windowing system.

## Installation
    > poetry install

On windows you may need to install the latest graphviz and run:

    pip install --global-option=build_ext --global-option="-IC:\Program Files\Graphviz\include" --global-option="-LC:\Program Files\Graphviz\lib" pygraphviz

`Qt.py` is a wrapper for common Qt backends, please make sure you install one yourself. Cypress was developed with PySide2. 

### Run
    > cypress

## To-do
- `asyncio` nodes
- node `ABCMeta`
- tests