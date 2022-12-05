import dearpygui.dearpygui as dpg

from cypress.editor.node.color import create_color_unit
from cypress.editor.node.script import create_script_node
from cypress.editor.graph.core import ChainGraph
from cypress.editor.graph.script import CodeGraph
from cypress.editor.utils import link_to_sender_receiver, parse_link_ints_to_str, parse_link_to_ints


class Editor:
    def __init__(self, window_size):
        self.id = None
        self.size = window_size

        self.eG = CodeGraph()

    def _execute_graph(self, sender, app_data):
        """ Callback to execute the editor's executable graph. """
        results = self.eG.execute()

        if not any(results):
            results = ""

        dpg.set_value("Execution.Output", results)


    def _link_callback(self, sender, link):
        """ Callback to link nodes in the editor. """
        sender, receiver = parse_link_to_ints(link)
        self.eG.add_link(sender, receiver, link)

        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(link[0], link[1], label=link, parent=self.id)

    def _delink_callback(self, sender, app_data):
        """ Callback to unlink nodes in the editor. """
        link = dpg.get_item_label(app_data)
        
        link = link_to_sender_receiver(link)
      
        if len(self.eG.nodes[sender]) == 1 and self.eG.nodes[sender] == ChainGraph.Sentinel:
            del(self.eG.nodes[sender])
        else:
            self.eG.nodes[sender].remove(link)

        # app_data -> link_id
        dpg.delete_item(app_data)

    def add_new_node(self, ty, pos, parent, name=None, chain=None):
        match ty:
            case 'Script':
                if name is None:
                    name = "Script Node"
                new_node = create_script_node(name, pos=pos, parent=parent)
                self.eG.nodes[new_node] = [ChainGraph.Sentinel]
            case 'Color':
                # TODO: integrate with executable graph - disjoint 
                if name is None:
                    name = "Color Node"
                new_node = create_color_unit(name, pos=pos, parent=parent)
            case _:
                return 
        
        if chain is not None:
            self._link_callback(new_node, parse_link_ints_to_str((new_node, chain)))

    def _add_new_node_callback(self, sender, app_data, pos=None):
        """ Callback to add a new node in the editor. """
        if pos is None:
            pos = self.size[0] / 2, self.size[1] / 2

        print(pos)
        self.add_new_node(app_data, pos, self.id)

    # delete selected node
    def _delete_selection(self, sender, app_data):
        """ Callback to delete all selected items in editor. """
        links = dpg.get_selected_links(self.id)
        for link in links:
            n1 = int(dpg.get_item_label(link).split(",")[0].strip("(").strip('\'').split('.')[0], 10)
            self._delink_callback(n1, link)

        nodes = dpg.get_selected_nodes(self.id)
        for node in nodes:
            del(self.eG.nodes[node])
            dpg.delete_item(node)


