import dearpygui.dearpygui as dpg


def create_color_unit(
    name: str,
    size = (150, 150),
    pos: tuple[float, float] = (0, 0),
    parent = None,
    type = "Simple"
):
    print(pos)
    with dpg.node(label="Color", pos=pos, parent=parent) as n_id:
        # TODO: as it stands, In/Out is for .Code execution flow.
        # I would like to create a meta node, but following a purely organic approach - 
        # the current functionality of nodes is not unified.
        #
        # ideally using an ABC, we standardize In/Out and generalize the statics.
        # Then, in the graph, we execute a generic function that passes from In to Out 
        # and executes statics associated with the node.
        dpg.add_node_attribute(tag=f"{n_id}.In", attribute_type=dpg.mvNode_Attr_Input)
        dpg.add_node_attribute(tag=f"{n_id}.Out", attribute_type=dpg.mvNode_Attr_Output)


        # The color selection should be converted to a python tuple and sent through Out.
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_color_edit(tag=f"{n_id}.Color", color=(255, 255, 255, 255), width=150)