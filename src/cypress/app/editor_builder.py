from contextlib import contextmanager
import logging
from typing import Any, Callable, List, Union, Tuple
import dearpygui.dearpygui as dpg
import dearpygui._dearpygui as internal_dpg

from cypress.editor.node.script import create_script_node
from cypress.editor.editor import Editor
from cypress.editor.utils import parse_link_ints_to_str


logger = logging.getLogger(__name__)


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
    def build_output_window(editor):
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

    @staticmethod
    @contextmanager
    def build(*, parent=None, editor=None, initializer=init_script_nodes_demo_graph, window_size=(1280,720), label: str =None, user_data: Any =None, 
                use_internal_label: bool =True, tag: Union[int, str] =0, width: int =0, height: int =0, indent: int =-1, show: bool =True, pos: Union[List[int], Tuple[int, ...]] =[], 
                delay_search: bool =False, min_size: Union[List[int], Tuple[int, ...]] =[100, 100], max_size: Union[List[int], Tuple[int, ...]] =[30000, 30000], menubar: bool =False, 
                collapsed: bool =False, autosize: bool =False, no_resize: bool =False, no_title_bar: bool =False, no_move: bool =False, no_scrollbar: bool =False, no_collapse: bool =False, 
                horizontal_scrollbar: bool =False, no_focus_on_appearing: bool =False, no_bring_to_front_on_focus: bool =False, no_close: bool =False, no_background: bool =False, 
                modal: bool =False, popup: bool =False, no_saved_settings: bool =False, no_open_over_existing_popup: bool =True, on_close: Callable =None, **kwargs
            ) -> Union[int, str]:
        """ Builds the main cyprus editor window. """
        if editor is None:
            editor = Editor(window_size=window_size)
        else:
            editor.size = window_size

        try:
            if parent is None:
                win_id = internal_dpg.add_window(label=label, user_data=user_data, use_internal_label=use_internal_label, tag=tag, 
                width=width, height=height, indent=indent, show=show, pos=pos, 
                delay_search=delay_search, min_size=window_size, max_size=max_size, 
                menubar=menubar, collapsed=collapsed, autosize=autosize, 
                no_resize=no_resize, no_title_bar=no_title_bar, no_move=no_move, 
                no_scrollbar=no_scrollbar, no_collapse=no_collapse, horizontal_scrollbar=horizontal_scrollbar, 
                no_focus_on_appearing=no_focus_on_appearing, no_bring_to_front_on_focus=no_bring_to_front_on_focus, 
                no_close=no_close, no_background=no_background, modal=modal, popup=popup, 
                no_saved_settings=no_saved_settings, no_open_over_existing_popup=no_open_over_existing_popup, on_close=on_close, **kwargs)
                internal_dpg.push_container_stack(win_id)

                parent=win_id

            with dpg.node_editor(callback=editor._link_callback, 
                    parent=parent,
            ) as editor.id:
                initializer(editor)

            yield editor
        finally:
            internal_dpg.pop_container_stack()