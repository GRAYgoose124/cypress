import logging

from NodeGraphQt import NodeGraph


logger = logging.getLogger(__name__)


class ChainGraph(NodeGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.output = "Final"

        self._chains = []
        self.__updated = False

    # chain
    def _get_chain_roots(self, end, roots=None, visited=None):
        """ Get all roots which contribute to a chain's final node. """
        if roots is None:
            roots = []
        if visited is None:
            visited = []

        prev_links = end.connected_input_nodes()
        if len(prev_links) == 0:
            roots.append(end)
            visited.append(end)
        else:
            for prev in prev_links:
                if prev not in visited:
                    self._get_chain_roots(prev, roots, visited)

        return roots
    
    def _all_chain_roots(self):
        """ Returns a list of all chain roots in the graph. """
        roots = []
        for node in self.all_nodes():
            if len(node.connected_output_nodes()) == 0:
                roots.append(node)

        return roots

    @property
    def chains(self):
        """ Returns a list of chains in the graph. 

        A chain is a list of nodes which are connected in a linear fashion.

        Several chains can exist in a graph and can intersect with each other.
        """
        if self.__updated:
            self._chains = self._all_chain_roots()
        
        return self._chains

    # executable
    def _exe_func(self, current, context):
        code = current.code

        if code is None:
            return context
            
        try:
            exec(code, context)
        # This naively fails on end nodes if one of their subchains has not been resolved.
        # TODO: Custom exception?
        except NameError:
            print(f"NameError {context[self.output]}")
            return context
        
        return context

    def execute_chain(self, current, ctx=None):
        """ Given a node, execute the chain of nodes that follow it. 
        
        """
        if ctx is not None:
            context = ctx
        else:
            context = {self.output: None}
       
        new_ctx = self._exe_func(current, context)
        if new_ctx is None:
            return context

        for node in current.connected_output_nodes():
            self.execute_chain(node, ctx=context)
    
        return context

    def execute(self):
        """ Executes the graph as a set of chains. """
        contexts = []

        logger.debug(f"execute.{self.chains=}")

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

        logger.debug(f"execute.{contexts=}")

        results = [f"{context[self.output]}" if context is not None else "OOPS" for context in contexts]

        print(results)
        return results