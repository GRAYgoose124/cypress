import dearpygui.dearpygui as dpg

from cypress.node.script_node import create_script_node
from cypress.graph_editor.graph import ExecutableGraph

def link_to_sender_receiver(link):
    link = link.split("\'")

    sender = link[1]
    receiver = link[3]

    return sender, receiver

def parse_link_to_ints(link):
    sender = int(link[0].split(".")[0], 10)
    receiver = int(link[1].split(".")[0], 10)

    return sender, receiver

def parse_link_ints_to_str(link):
    sender_id, receiver_id = link
    return f"{sender_id}.Out", f"{receiver_id}.In"


class Editor:
    def __init__(self, window_size):
        self.id = None
        self.size = window_size

        self.G = ExecutableGraph()

    def _execute_graph(self, sender, app_data):
        results = self.G.execute()

        dpg.set_value("Execution.Output", [f"{context['Final']}" for context in results])


    def _link_callback(self, sender, link):
        sender, receiver = parse_link_to_ints(link)
        self.G.add_link(sender, receiver, link)

        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(link[0], link[1], label=link, parent=self.id)

    def _delink_callback(self, sender, app_data):
        link = dpg.get_item_label(app_data)
        
        link = link_to_sender_receiver(link)
        link = parse_link_to_ints(link)
        link = parse_link_ints_to_str(link)
    
        self.G.script_nodes[sender].remove(link)
        # app_data -> link_id
        dpg.delete_item(app_data)

    def _add_new_node(self, sender, app_data):
        pos = self.size[0] / 2, self.size[1] / 2
        new_node = create_script_node("Script Node", pos, parent=self.id)
        self.G.script_nodes[new_node] = []

    # delete selected node
    def _delete_selection(self, sender, app_data):
        links = dpg.get_selected_links(self.id)
        for link in links:
            n1 = int(dpg.get_item_label(link).split(",")[0].strip("(").strip('\'').split('.')[0], 10)
            self._delink_callback(n1, link)

        nodes = dpg.get_selected_nodes(self.id)
        for node in nodes:
            if node == self.G.root:
                self.G.root = self.G.script_nodes[node][1]
            dpg.delete_item(node)

    def _close_app_callback(self):
        # close the window
        dpg.stop_dearpygui()


class EditorBuilder:
    @staticmethod
    def _empty_script_node_chain(editor, n: int):
        last = None
        for i in range(n):
            node = create_script_node(f"Script Node {i}", (i * 200, 0), parent=editor.id)
            
            if last is not None:
                link = f"{last}.Out", f"{node}.In"
                editor._link_callback(last, link)
        
            last = node

    @staticmethod
    def build(window_size):
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
                        EditorBuilder._empty_script_node_chain(editor, 3)

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