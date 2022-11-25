import dearpygui.dearpygui as dpg

from cypress.graph_editor.builder import EditorBuilder, init_test_graph


class App:
    def __init__(self) -> None:  
        self.title = "Cypress"
        self.size = (1280, 720)
        
        self.editor = None

    def run(self):
        dpg.create_context()

        with dpg.window(label=self.title, width=self.size[0], height=self.size[1], 
            no_bring_to_front_on_focus=True, no_move=True, on_close=self._close_app_callback, 
        ) as main_window_id:
            with dpg.group(horizontal=True):
                self.editor = EditorBuilder.build(main_window_id, self.size)

                dpg.add_button(label="Execute", callback=self.editor._execute_graph)
                dpg.add_button(label="Add", callback=self.editor._add_new_node)
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

