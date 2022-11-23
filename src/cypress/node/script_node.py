import dearpygui.dearpygui as dpg


def create_script_node(
    name: str,
    pos: tuple[float, float] = (0, 0),
    parent = None
):
    size = (100, 100)
    with dpg.node(label=name, pos=pos, parent=parent) as n_id:
        dpg.add_node_attribute(tag=f"{n_id}.In", attribute_type=dpg.mvNode_Attr_Input)
        dpg.add_node_attribute(tag=f"{n_id}.Out", attribute_type=dpg.mvNode_Attr_Output)

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_input_text(tag=f"{n_id}.Code", multiline=True, width=size[0], height=size[1])
            
        return n_id
  

