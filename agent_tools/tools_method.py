from pydantic import BaseModel
from pydantic import create_model
from typing import Callable
import inspect
class Tools:
    def __init__(self):
        self._tools={}
        self._tool_method_schema={}
        self._tool_method={}
    
    def add_tool(self,method:Callable):
        '''make the agent aware of the method as a callable tool'''
        fields={}
        sig = inspect.signature(method)
        for param in sig.parameters.values():
            if param.annotation is inspect.Parameter.empty:
                raise ValueError(f"All parameters must have type annotations. Missing for parameter: {param.name} in method: {method.__name__}")
            if param.default is inspect.Parameter.empty:
                fields[param.name] = (param.annotation, ...)
            else:
                fields[param.name] = (param.annotation, param.default)
        method_schema = create_model(f"{method.__name__}_schema", **fields)
        self._tools[method.__name__]=method.__doc__
        self._tool_method_schema[method.__name__]=method_schema
        self._tool_method[method.__name__]=method
        return method #returning the method so orignal functionality is not lost, and it can be used as a normal function as well
        
    def get_tools(self):
        return self._tools
    
    def get_tool_info(self):
        return list(self._tools.items())
    
    def get_tool_method_schema(self,method_name:str):
        return self._tool_method_schema[method_name]

        