from cypress.editor.graph.core import ChainGraph


class ExecutableGraph(ChainGraph):
    def __init__(self) -> None:
        super().__init__()

        self.output = None

    def _exe_func(self):
        """ Updates the executable graph context appropriately or returns None if failure. """
        raise NotImplementedError

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

        results = [f"{context[self.output]}" if context is not None else "OOPS" for context in contexts]
        return results