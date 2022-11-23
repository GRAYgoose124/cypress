from pathlib import Path
import dearpygui.dearpygui as dpg

from cypress.graphbuilder import EditorGraphBuilder


class App:
    def __init__(self) -> None:  
        self.title = "Cypress"
        self.size = (1280, 720)
        self.editor = EditorGraphBuilder(self.size)

    def run(self):
        dpg.create_context()

        self.editor.build()

        dpg.create_viewport(title=self.title, width=self.size[0], height=self.size[1])

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()