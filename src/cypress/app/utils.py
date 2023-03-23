from NodeGraphQt import NodeGraph


def build_demo_graph(graph: NodeGraph):
        def create_node(label, pos):
            node = graph.create_node(
                'cypress.nodes.ScriptNode', name=f'Script Node {label}', pos=pos)
            return node

        s1 = create_node(1, [0, 0])
        s2 = create_node(2, [400, 0])
        s2b = create_node("2B", [400, 200])
        s3 = create_node(3, [800, 0])
        s3b = create_node("3B", [800, 200])

        output = graph.create_node(
            'cypress.nodes.SimpleOutputNode', name='Output', pos=[800, 600])

        s1.code = "print('Hello from Script Node 1!')\na=5"
        s2.code = "print('Hello from Script Node 2!')\nb=10"
        s3.code = "print('Hello from Script Node 3!')\nc=a+b\nprint(c)"

        s2b.code = "print('Hello from Script Node 2B!')\nd=20"
        s3b.code = "print('Hello from Script Node 3B!')\nFinal=c+d\nprint(Final)"

        s1.set_output(0, s2.input(0))
        s1.set_output(0, s2b.input(0))

        s2.set_output(0, s3.input(0))
        s2b.set_output(0, s3b.input(0))
        s3.set_output(0, s3b.input(0))

        s3b.set_output(0, output.input(0))

        graph.select_all()
        graph.auto_layout_nodes()
        graph.fit_to_selection()
        graph.clear_selection()