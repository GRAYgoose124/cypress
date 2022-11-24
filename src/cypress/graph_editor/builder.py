import dearpygui.dearpygui as dpg

from cypress.node.script_node import create_script_node
from cypress.graph_editor.editor import Editor
from cypress.graph_editor.utils import parse_link_ints_to_str


def init_test_graph(editor):
    n = 3
    last = EditorBuilder._empty_script_node_chain(editor, n)

    parallel_node = create_script_node(f"Parallel", (25 + (n-2) * 150, 200), parent=editor.id)
    editor.G.script_nodes[parallel_node] = []
    editor._link_callback(parallel_node, parse_link_ints_to_str((parallel_node, last)))
    
    orphan_node = create_script_node(f"Orphan", (25 + (n-2) * 150, 400), parent=editor.id)
    editor.G.script_nodes[orphan_node] = []


class EditorBuilder:
    @staticmethod
    def _empty_script_node_chain(editor, n: int):
        last = None
        for i in range(n):
            node = create_script_node(f"Script Node {i}", (25 + i * 150, 25), parent=editor.id)
            
            if last is not None:
                link = f"{last}.Out", f"{node}.In"
                editor._link_callback(last, link)
        
            last = node
        
        return last

    @staticmethod
    def build(window_size, initializer=init_test_graph):
        """ Builds the main cyprus editor window. """
        editor = Editor(window_size=window_size)

        with dpg.window(label="Editor", width=window_size[0], height=window_size[1], no_bring_to_front_on_focus=True, on_close=editor._close_app_callback):
            with dpg.group():
                with dpg.group(horizontal=True):
                    with dpg.group():
                        dpg.add_button(label="Execute", callback=editor._execute_graph)
                        dpg.add_button(label="Add", callback=editor._add_new_node)
                        dpg.add_button(label="Delete", callback=editor._delete_selection)

                    with dpg.node_editor(callback=editor._link_callback, 
                            
                            height=editor.size[1] - 50
                    ) as editor_id:
                        editor.id = editor_id
                        initializer(editor)

            out_w = editor.size[0]/2
            out_h = editor.size[1]/4
            bottom_left = editor.size[0]-out_w, editor.size[1]-out_h
            with dpg.window(label="Cypress Output", 
                            width=out_w, 
                            height=out_h, 
                            pos=bottom_left,
                            no_close=True
            ):
                dpg.add_text(tag="Execution.Output")
        
        return editor