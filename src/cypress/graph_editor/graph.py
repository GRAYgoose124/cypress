import dearpygui.dearpygui as dpg


class ScriptGraph:
    def __init__(self) -> None:
        self.script_nodes = {}

    def get_prev_link(self, node):
        prev = None
        for link in self.script_nodes.values():
            if link is not None:
                l0 = int(link[0].strip("(").strip('\'').split('.')[0], 10)
                l1 = int(link[1].strip(")").strip('\'').split('.')[0], 10)
                if l1 == node:
                    prev = l0

        return prev

    def get_next_link(self, node):
        link = self.script_nodes[node]
        if link is not None:
            return int(link[1].split(".")[0], 10)
        else:
            return None

    def _find_chain_roots(self):
        ends = []

        for node, link in self.script_nodes.items():
            if link is None:
                ends.append(node)
        
        roots = []
        for end in ends:
            prev_link = end
            to_save = prev_link
            while prev_link is not None:
                to_save = prev_link
                prev_link = self.get_prev_link(prev_link)
            roots.append(to_save)

        return roots

    @property
    def chains(self):
        return self._find_chain_roots()


class ExecutableGraph(ScriptGraph):
    def __init__(self) -> None:
        super().__init__()

    def execute_chain(self, root):
        context = {'Final': None}

        current = root
        while current is not None:
            code = dpg.get_value(f"{current}.Code")
            exec(code, context)

            current = self.get_next_link(current)
        
        return context

    def execute(self):
        contexts = []

        # TODO: Execute all contexts which flow into a final node.
        # Later MIMO will be supported.
        for root in self.chains:
            new_context = self.execute_chain(root)
            contexts.append(new_context)

        return contexts