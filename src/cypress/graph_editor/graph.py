from logging import root
from cypress.graph_editor.utils import parse_link_ints_to_str, parse_link_to_ints
import dearpygui.dearpygui as dpg


class ScriptGraph:
    def __init__(self) -> None:
        self.script_nodes = {}

    def add_link(self, sender, receiver, link):
        """ Add a link between two script nodes. """
        if sender in self.script_nodes:
            self.script_nodes[sender].append(link)
        else:
            self.script_nodes[sender] = [link]

        if receiver not in self.script_nodes:
            self.script_nodes[receiver] = []

    def get_next_links(self, node):
        """ Get all nodes which the given node outputs to. """
        next_links = []
        # Look for another node acting as a receiver for this node as a sender
        for n, links in self.script_nodes.items():
            for link in links:
                l0, l1 = parse_link_to_ints(link)
                if l0 == node:
                    next_links.append(l1)
        
        return next_links

    def get_prev_links(self, node):
        """ Get all nodes which input into the given node. """
        prev_links = []
        for n, links in self.script_nodes.items():
            for link in links:
                l0, l1 = parse_link_to_ints(link)
                if l1 == node:
                    # prob should use l0
                    prev_links.append(n)

        return prev_links

    def _get_chain_roots(self, end, roots=None):
        """ Get all roots which contribute to a chain's final node. """
        if roots is None:
            roots = []

        prev_links = self.get_prev_links(end)
        if len(prev_links) == 0:
            roots.append(end)
        else:
            for prev in prev_links:
                self._get_chain_roots(prev, roots)

        return roots
        
    def _all_chain_roots(self):
        """ Internal method to find all chains of this graph. """
        ends = []
        for node, links in self.script_nodes.items():
            if len(links) == 0:
                ends.append(node)
        
        root_nodes = []
        for final_node in ends:
            root_nodes.append(self._get_chain_roots(final_node))

        return root_nodes

    @property
    def chains(self):
        """ Get all chains of this graph. 

            A chain is a depth-first tree path, it can have multiple roots, but only one final node.
            (TODO: Multiple final nodes?)
        """ 
        return self._all_chain_roots()


class ExecutableGraph(ScriptGraph):
    def __init__(self) -> None:
        super().__init__()

    def execute_chain(self, current, ctx=None):
        """ Given a node, execute the chain of nodes that follow it. """
        if ctx is not None:
            context = ctx
        else:
            context = {'Final': None}
       
        code = dpg.get_value(f"{current}.Code")

        try:
            exec(code, context)
        except NameError:
            print(f"NameError {context['Final']=}")
            return context

        for node in self.get_next_links(current):
            self.execute_chain(node, context)
    
        return context

    def execute(self):
        """ Executes the graph as a set of chains. """
        contexts = []

        for roots in self.chains:
            context = None
            if isinstance(roots, int):
                context = self.execute_chain(roots)
            else:
                context = None
                for root in roots:
                    if context is None:
                        context = self.execute_chain(root)
                    else:
                        context.update(self.execute_chain(root, context))

            contexts.append(context)

        return contexts