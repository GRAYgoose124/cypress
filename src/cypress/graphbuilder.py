from typing_extensions import Self
import dearpygui.dearpygui as dpg
from cypress.node.script_node import create_script_node


class EditorGraphBuilder:
    def __init__(self, size):
        self.id = None
        self.size = size

        self.root = None
        self.script_nodes = None

    def _empty_script_node_chain(self, n: int):
        last = None
        root = None
        for i in range(n):
            node = create_script_node(f"Script Node {i}", (i * 200, 0))
            
            if last is not None:
                link = f"{last}.Out", f"{node}.In"
                self._link_callback(last, link)
            else:
                root = node
        
            last = node

        return root

    # callback runs when user attempts to connect attributes
    def _link_callback(self, sender, link):
        self.script_nodes[sender] = link
        self.script_nodes[int(link[1].split(".")[0], 10)] = None

        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(link[0], link[1])

    # callback runs when user attempts to disconnect attributes
    def _delink_callback(self, sender, app_data):
        self.script_nodes[sender] = None
        # app_data -> link_id
        dpg.delete_item(app_data)

    def execute(self, sender, app_data):
        print("Executing Script Nodes")
        
        root = self.root
        current = root
        while current is not None:
            code = dpg.get_value(f"{current}.Code")
            print(current, code)

            link = self.script_nodes[current]
            if link is not None:
                current = int(link[1].split(".")[0], 10)
            else:
                break

    def build(self):
        self.script_nodes = {}

        # place two children side by side
        with dpg.window(label="Editor", width=self.size[0], height=self.size[1]) as w_id:
            # use a table to create two columns
            with dpg.group(horizontal=True):
                dpg.add_button(label="Execute", callback=self.execute)

                with dpg.node_editor(callback=self._link_callback, 
                        delink_callback=self._delink_callback
                ) as editor_id:
                    self.id = editor_id
                    self.root = self._empty_script_node_chain(3)
            
