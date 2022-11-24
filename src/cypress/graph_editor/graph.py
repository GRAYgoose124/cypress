import dearpygui.dearpygui as dpg


class ScriptGraph:
    def __init__(self) -> None:
        self.script_nodes = {}

    def _find_prev_link(self, node):
        prev = None
        for link in self.script_nodes.values():
            if link is not None:
                l0 = int(link[0].strip("(").strip('\'').split('.')[0], 10)
                l1 = int(link[1].strip(")").strip('\'').split('.')[0], 10)
                if l1 == node:
                    prev = l0

        return prev

    def _find_chain_roots(self):
        ends = []

        for node, link in self.script_nodes.items():
            if link is None:
                ends.append(node)
        
        roots = []
        for end in ends:
            prev_link = end
            while prev_link is not None:
                prev_link = self._find_prev_link(prev_link)
            roots.append(prev_link)

        return roots

    @property
    def chains(self):
        return self._find_chain_roots()


class ExecutableGraph(ScriptGraph):
    def __init__(self) -> None:
        super().__init__()

    def execute_chain(self, root):
        visited = set()

        context = {'Final': None}

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

            visited.add(current)

        return visited, context

    def execute(self, sender, app_data):
        visited = set()
        contexts = []

        for root in self.chains:
            now_visited, new_context = self.execute_chain(root)
            visited.update(now_visited)
            contexts.append(new_context)

        # TODO: move to Editor 
        # Update output window
        dpg.set_value("Execution.Output", [f"{context['Final']}\n" for context in contexts])
