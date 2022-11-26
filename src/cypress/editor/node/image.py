import dearpygui.dearpygui as dpg


def directory_select():
    pass

def create_color_unit(
    name: str,
    size = (150, 150),
    pos: tuple[float, float] = (0, 0),
    parent = None
):
    with dpg.node(label="Image", pos=pos, parent=parent) as n_id:
        dpg.add_node_attribute(tag=f"{n_id}.In", attribute_type=dpg.mvNode_Attr_Input)
        dpg.add_node_attribute(tag=f"{n_id}.Out", attribute_type=dpg.mvNode_Attr_Output)

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_input_text(tag=f"{n_id}.Image", multiline=True, width=size[0], height=size[1])

        return n_id
  

