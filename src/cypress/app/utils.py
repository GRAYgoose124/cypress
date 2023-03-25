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

        in_node = graph.create_node(
            'cypress.nodes.SimpleInputNode', name='Input', pos=[0, 300])
        
        s1.set_input(0, in_node.output(0))

        output = graph.create_node(
            'cypress.nodes.SimpleOutputNode', name='Output', pos=[800, 600])

        image = graph.create_node(
            'cypress.nodes.ImageNode', name='Image', pos=[0, 600])

        # This demo string creates a figure to later be displayed in the output node.
        demo_matplotlib_figure = """
import matplotlib.pyplot as plt
import numpy as np
# create a figure and store in var
fig = plt.figure()
# draw a line plot to the figure
fig.add_subplot(111).plot(np.random.rand(10))
"""

        s1.code = "print('Hello from Script Node 1!')\na=5\n\n#print(Input)"
        s2.code = "print('Hello from Script Node 2!')\nb=10"
        s3.code = "print('Hello from Script Node 3!')\nc=a+b\nprint(c)" + demo_matplotlib_figure

        s2b.code = "print('Hello from Script Node 2B!')\nd=20"
        s3b.code = "print('Hello from Script Node 3B!')\nFinal=c+d\nprint(Final)\nImage = fig"


        s1.set_output(0, s2.input(0))
        s1.set_output(0, s2b.input(0))

        s2.set_output(0, s3.input(0))
        s2b.set_output(0, s3b.input(0))
        s3.set_output(0, s3b.input(0))

        s3b.set_output(0, output.input(0))
        image.set_input(0, s3b.output(0))

        graph.select_all()
        graph.auto_layout_nodes()
        graph.fit_to_selection()
        graph.clear_selection()