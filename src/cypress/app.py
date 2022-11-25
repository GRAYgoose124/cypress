from typing_extensions import Self
import dearpygui.dearpygui as dpg

from cypress.graph_editor.builder import EditorBuilder, init_script_nodes_demo_graph


class App:
    def __init__(self) -> None:  
        self.title = "Cypress"
        self.size = (1280, 720)
        
        self.editor = None

        self._selected_node = "Script"

    def run(self):
        dpg.create_context()

        with dpg.window(label=self.title, width=self.size[0], height=self.size[1], 
            no_bring_to_front_on_focus=True, no_move=True, on_close=self._close_app_callback, 
        ) as main_window_id:
            with dpg.group():
                self.editor = EditorBuilder.build(main_window_id, self.size)

                dpg.add_button(label="Execute", callback=self.editor._execute_graph)

                # TODO: Generate list from .node abc instances.
                node_options = ("Script", "Color")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add", callback=lambda s, ad: self.editor._add_new_node_callback(s, self.selected_node))
                    dpg.add_combo(node_options, no_preview=True, default_value="Script", callback=lambda s, ad: setattr(self, '_selected_node', ad))

        
                dpg.add_button(label="Delete", callback=self.editor._delete_selection)

        dpg.create_viewport(title=self.title, width=self.size[0], height=self.size[1])

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    @staticmethod
    def _close_app_callback():
        """ Callback for closing the app with DearPyGUI. """
        # close the window
        dpg.stop_dearpygui()


    @property
    def selected_node(self):
        return self._selected_node