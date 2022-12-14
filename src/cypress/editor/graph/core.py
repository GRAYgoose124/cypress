import logging
import dearpygui.dearpygui as dpg

from cypress.editor.utils import parse_link_ints_to_str, parse_link_to_ints


logger = logging.getLogger(__name__)


class ExecutableGraphCycle(Exception):
    pass


class ChainGraph:
    Sentinel = (0xDEAD, 0xBEEF)

    def __init__(self) -> None:
        self.nodes = {}

    def add_link(self, sender, receiver, link):
        """ Add a link between two script nodes. """
        if sender in self.nodes:
            self.nodes[sender].append(link)
        else:
            self.nodes[sender] = [link, ChainGraph.Sentinel]

        if receiver not in self.nodes:
            self.nodes[receiver] = [ChainGraph.Sentinel]

    def get_next_links(self, node):
        """ Get all nodes which the given node outputs to. """
        next_links = []
        # Look for another node acting as a receiver for this node as a sender
        for n, links in self.nodes.items():
            for link in links:
                if link == ChainGraph.Sentinel:
                    continue
                
                l0, l1 = parse_link_to_ints(link)
                if l0 == node:
                    next_links.append(l1)
        
        return next_links

    def get_prev_links(self, node):
        """ Get all nodes which input into the given node. """
        prev_links = []
        for n, links in self.nodes.items():
            for link in links:
                if link == ChainGraph.Sentinel:
                    continue

                l0, l1 = parse_link_to_ints(link)
                if l1 == node:
                    # prob should use l0
                    prev_links.append(n)

        logger.debug(f"get_prev_links.{prev_links=}")

        return prev_links

    def _get_chain_roots(self, end, roots=None, visited=None):
        """ Get all roots which contribute to a chain's final node. """
        if roots is None:
            roots = []
        if visited is None:
            visited = []

        prev_links = self.get_prev_links(end)
        if len(prev_links) == 0:
            roots.append(end)
            visited.append(end)
        else:
            for prev in prev_links:
                if prev not in visited:
                    visited.append(prev)
                    self._get_chain_roots(prev, roots=roots, visited=visited)
                else:
                    logger.info(f"Cycle detected, final node: {end} failed.")
                    raise ExecutableGraphCycle

        return roots
        
    def _all_chain_roots(self):
        """ Internal method to find all chains of this graph. """
        ends = []
        for node, links in self.nodes.items():
            if len(links) == 1 and links[0] == ChainGraph.Sentinel:
                ends.append(node)
        
        root_nodes = []
        for final_node in ends:
            try:
                root_nodes.append(self._get_chain_roots(final_node))
            except ExecutableGraphCycle:
                continue

        logger.debug(f"_all_chain_roots.{root_nodes=}")

        return root_nodes

    @property
    def chains(self):
        """ Get all chains of this graph. 

            A chain is a depth-first tree path, it can have multiple roots, but only one final node.
            (TODO: Multiple final nodes?)
        """ 
        return self._all_chain_roots()

