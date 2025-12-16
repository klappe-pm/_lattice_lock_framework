import inspect
from collections.abc import Callable
from typing import Any


class FunctionCallHandler:
    def __init__(self):
        self._functions: dict[str, Callable] = {}

    def register_function(self, name: str, func: Callable):
        """Registers a function to be callable by the orchestrator."""
        if not callable(func):
            raise ValueError(f"Registered item '{name}' is not a callable function.")
        self._functions[name] = func

    async def execute_function_call(self, name: str, **kwargs) -> Any:
        """Executes a registered function with the given arguments."""
        func = self._functions.get(name)
        if not func:
            raise ValueError(f"Function '{name}' not registered.")

        # Assume function is async if it's an awaitable coroutine
        if inspect.iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)

    def get_registered_functions_metadata(self) -> dict[str, dict[str, Any]]:
        """
        Returns metadata for all registered functions, including parameter schemas.
        """
        metadata = {}
        for name, func in self._functions.items():
            sig = inspect.signature(func)
            parameters = {}
            for param_name, param in sig.parameters.items():
                param_info = {
                    "kind": str(param.kind),
                    "default": str(param.default)
                    if param.default != inspect.Parameter.empty
                    else None,
                    "annotation": str(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else None,
                }
                parameters[param_name] = param_info

            metadata[name] = {
                "name": name,
                "description": func.__doc__ or "No description provided.",
                "parameters": parameters,
            }
        return metadata
