import dearpygui.dearpygui as dpg

from cypress.app.editor_builder import EditorBuilder


class App:
    def __init__(self) -> None:  
        self.title = "Cypress"
        self.size = (1280, 720)
        
        self.editor = None

        self._selected_node = "Script"

    def run(self):
        dpg.create_context()

        with EditorBuilder.build(label="Editor", autosize=True, no_move=True, no_bring_to_front_on_focus=True, no_collapse=True, no_scrollbar=True, on_close=self._close_app_callback) as self.editor:
            with dpg.group():
                dpg.add_button(label="Execute", callback=self.editor._execute_graph)

                # TODO: Generate list from .node abc instances.
                node_options = ("Script", "Color")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add", callback=lambda s, ad: self.editor._add_new_node_callback(s, self.selected_node))
                    dpg.add_combo(node_options, no_preview=True, default_value="Script", callback=lambda s, ad: setattr(self, '_selected_node', ad))

        
                # dpg.add_button(label="Delete", callback=self.editor._delete_selection)
        EditorBuilder.build_output_window(self.editor)

        with dpg.handler_registry():
                dpg.add_key_press_handler(dpg.mvKey_Delete, callback=self.editor._delete_selection)

        dpg.create_viewport(title=self.title, width=self.size[0], height=self.size[1])

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    @staticmethod
    def _resize_app_callback():
        """ Ensures the internal editor is maximized in the main window. """


    @staticmethod
    def _close_app_callback():
        """ Callback for closing the app with DearPyGUI. """
        # close the window
        dpg.stop_dearpygui()


    @property
    def selected_node(self):
        return self._selected_node