import os
import dearpygui.dearpygui as dpg
import pyglfw.pyglfw as glfw

from cypress.node.script_node import create_script_node


class EditorGraphBuilder:
    def __init__(self, size):
        self.id = None
        self.size = size

        self.root = None
        self.script_nodes = None
        self.contexts = []

    def _empty_script_node_chain(self, n: int):
        last = None
        root = None
        for i in range(n):
            
            node = create_script_node(f"Script Node {i}", (i * 200, 0), parent=self.id)
            
            if last is not None:
                link = f"{last}.Out", f"{node}.In"
                self._link_callback(last, link)
            else:
                dpg.set_item_label(node, "Root")
                root = node
        
            last = node

        return root

    # callback runs when user attempts to connect attributes
    def _link_callback(self, sender, link):
        sender = int(link[0].split(".")[0], 10)
        receiver = int(link[1].split(".")[0], 10)
        self.script_nodes[sender] = link
        self.script_nodes[receiver] = None

        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(link[0], link[1], label=link, parent=self.id)

    # callback runs when user attempts to disconnect attributes
    def _delink_callback(self, sender, app_data):
        print("DELINK", sender)
        self.script_nodes[sender] = None
        # app_data -> link_id
        dpg.delete_item(app_data)

    def add_new_node(self, sender, app_data):
        pos = self.size[0] / 2, self.size[1] / 2
        new_node = create_script_node("Script Node", pos, parent=self.id)
        self.script_nodes[new_node] = None

    # delete selected node
    def delete_selection(self, sender, app_data):
        links = dpg.get_selected_links(self.id)
        for link in links:
            n1 = int(dpg.get_item_label(link).split(",")[0].strip("(").strip('\'').split('.')[0], 10)
            self._delink_callback(n1, link)

        nodes = dpg.get_selected_nodes(self.id)
        for node in nodes:
            if node == self.root:
                self.root = self.script_nodes[node][1]
            dpg.delete_item(node)
        
    def execute(self, sender, app_data):
        print("Executing Script Nodes")
        
        # create a python context for all nodes
        context = {'Final': None}

        root = self.root
        current = root
        while current is not None:
            code = dpg.get_value(f"{current}.Code")
            # execute code
            exec(code, context)

            link = self.script_nodes[current]
            if link is not None:
                current = int(link[1].split(".")[0], 10)
            else:
                break
        
        # Update output window
        dpg.set_value("Execution.Output", context['Final'])

    def _close_callback(self):
        # close the window
        dpg.stop_dearpygui()

    def build(self):
        self.script_nodes = {}

        with dpg.window(label="Editor", width=self.size[0], height=self.size[1], no_bring_to_front_on_focus=True, on_close=self._close_callback):
            with dpg.group():
                with dpg.group(horizontal=True):
                    with dpg.group():
                        dpg.add_button(label="Execute", callback=self.execute)
                        dpg.add_button(label="Add", callback=self.add_new_node)
                        dpg.add_button(label="Delete", callback=self.delete_selection)

                    with dpg.node_editor(callback=self._link_callback, 
                            
                            height=self.size[1] - 50
                    ) as editor_id:
                        self.id = editor_id
                        self.root = self._empty_script_node_chain(3)

            out_w = self.size[0]/2
            out_h = self.size[1]/4
            with dpg.window(label="Cypress Output", 
                            width=out_w, 
                            height=out_h, 
                            pos=(self.size[0]-out_w, self.size[1]-out_h),
                            no_close=True
            ):
                dpg.add_text(tag="Execution.Output")