import dearpygui.dearpygui as dpg

from cypress.node.color_unit import create_color_unit
from cypress.node.script_node import create_script_node
from cypress.graph_editor.graph import ExecutableGraph
from cypress.graph_editor.utils import link_to_sender_receiver, parse_link_ints_to_str, parse_link_to_ints


class Editor:
    def __init__(self, window_size):
        self.id = None
        self.size = window_size

        self.G = ExecutableGraph()

    def _execute_graph(self, sender, app_data):
        """ Callback to execute the editor's executable graph. """
        results = self.G.execute()

        dpg.set_value("Execution.Output", [f"{context['Final']}" for context in results])

    def _link_callback(self, sender, link):
        """ Callback to link nodes in the editor. """
        sender, receiver = parse_link_to_ints(link)
        self.G.add_link(sender, receiver, link)

        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(link[0], link[1], label=link, parent=self.id)

    def _delink_callback(self, sender, app_data):
        """ Callback to unlink nodes in the editor. """
        link = dpg.get_item_label(app_data)
        
        link = link_to_sender_receiver(link)
        link = parse_link_to_ints(link)
        link = parse_link_ints_to_str(link)
    
        self.G.script_nodes[sender].remove(link)
        # app_data -> link_id
        dpg.delete_item(app_data)

    def _add_new_node(self, sender, app_data):
        """ Callback to add a new node in the editor. """
        pos = self.size[0] / 2, self.size[1] / 2

        match app_data:
            case 'Script':
                new_node = create_script_node("Script Node", pos, parent=self.id)
            case 'Color':
                new_node = create_color_unit("Color Node", pos, parent=self.id)
            case _:
                return 

        self.G.script_nodes[new_node] = []

    # delete selected node
    def _delete_selection(self, sender, app_data):
        """ Callback to delete all selected items in editor. """
        links = dpg.get_selected_links(self.id)
        for link in links:
            n1 = int(dpg.get_item_label(link).split(",")[0].strip("(").strip('\'').split('.')[0], 10)
            self._delink_callback(n1, link)

        nodes = dpg.get_selected_nodes(self.id)
        for node in nodes:
            dpg.delete_item(node)


