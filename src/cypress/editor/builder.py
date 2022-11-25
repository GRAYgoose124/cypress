import dearpygui.dearpygui as dpg

from cypress.editor.node.script_node import create_script_node
from cypress.editor.editor import Editor
from cypress.editor.utils import parse_link_ints_to_str


def init_script_nodes_demo_graph(editor, n=3):
    """ Initialize a graph of script nodes for editor default workspace. """
    size = (150, 200)
    offset = (50, 50)

    chain = EditorBuilder._empty_script_node_chain(editor, n, size=size, offset=offset)
    pos = ((n-2) * size[0] + offset[0]*2, size[1] + offset[1]*2)
    pos2 = (2.5 * pos[0], pos[1])
    editor.add_new_node("Script", pos=pos, parent=editor.id, name="Parallel", chain=chain)
    editor.add_new_node("Script", pos=pos2, parent=editor.id, name="Orphan")


class EditorBuilder:
    @staticmethod
    def _empty_script_node_chain(editor, n: int, size = (150, 200), offset = (50, 50)):
        """ Build a default chain of nodes, singly-linked in `editor`. """
        last = None
        for i in range(n):
            node = create_script_node(f"Script Node {i}", pos=((size[0]+offset[0]*2)*i+offset[0], offset[1]), parent=editor.id)
            
            if last is not None:
                link = f"{last}.Out", f"{node}.In"
                editor._link_callback(last, link)
        
            last = node
        
        return last

    @staticmethod
    def build(parent, window_size, editor=None, initializer=init_script_nodes_demo_graph):
        """ Builds the main cyprus editor window. """
        if editor is None:
            editor = Editor(window_size=window_size)
        else:
            editor.size = window_size

        with dpg.window(label="Editor", width=window_size[0], height=window_size[1],
            no_bring_to_front_on_focus=True, no_move=True, no_resize=True, no_title_bar=True,
        ):

            with dpg.node_editor(callback=editor._link_callback, 
                    height=editor.size[1] - 50,
                    parent=parent,
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