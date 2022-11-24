from logging import root
import dearpygui.dearpygui as dpg


class ScriptGraph:
    def __init__(self) -> None:
        self.script_nodes = {}

    def add_link(self, sender, receiver, link):
        if sender in self.script_nodes:
            self.script_nodes[sender].append(link)
        else:
            self.script_nodes[sender] = [link]

        if receiver not in self.script_nodes:
            self.script_nodes[receiver] = []

    def get_next_link(self, node):
        link = self.script_nodes[node]
        if len(link):
            return int(link[1].split(".")[0], 10)
        else:
            return None

    def get_prev_links(self, node):
        prev_links = []
        for links in self.script_nodes.values():
            if links is not None:
                for link in links:
                    # todo use parse_to_ints
                    l0 = int(link[0].strip("(").strip('\'').split('.')[0], 10)
                    l1 = int(link[1].strip(")").strip('\'').split('.')[0], 10)
                    print(f"{l0=}, f{l1=}")
                    if l1 == node:
                        prev_links.append(l0)

                return prev_links

    def _get_chain_roots(self, end, roots=None):
        if roots is None:
            roots = []

        prev_links = self.get_prev_links(end)
        print(f"{prev_links=}")
        if len(prev_links) == 0:
            roots.append(end)
            return end
        else:
            for link in prev_links:
                return self._get_chain_roots(link, roots)

    def _find_chain_roots(self):
        ends = []
        for node, links in self.script_nodes.items():
            if len(links) == 0:
                ends.append(node)
        
        root_nodes = []
        for final_node in ends:
            root_nodes.append(self._get_chain_roots(final_node))

        print(f"{root_nodes=}")
        return root_nodes

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
        for roots in self.chains:
            print(roots)
            context = {}
            if isinstance(roots, int):
                context = self.execute_chain(roots)
            else:
                print(roots)
                ctx = {}
                for root in roots:
                    context.update(self.execute_chain(root))
                    print(f"{root}: {ctx['Final']=}")



            contexts.append(context)

        return contexts