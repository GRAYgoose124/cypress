import dearpygui.dearpygui as dpg

from cypress.editor.graph.executable import ExecutableGraph


class CodeGraph(ExecutableGraph):
    def __init__(self) -> None:
        super().__init__()
        self.output = "Final"

    def _exe_func(self, current, context):
        code = dpg.get_value(f"{current}.Code")

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