import asyncio
import inspect
import logging
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class FunctionCallHandler:
    """
    Handles secure execution of registered functions with sandboxing and validation.
    """

    def __init__(self, execution_timeout: float = 30.0):
        self._functions: dict[str, Callable] = {}
        self.execution_timeout = execution_timeout

    def register_function(self, name: str, func: Callable):
        """Registers a function to be callable by the orchestrator."""
        if not callable(func):
            raise ValueError(f"Registered item '{name}' is not a callable function.")
        self._functions[name] = func

    async def execute_function_call(self, name: str, **kwargs) -> Any:
        """Executes a registered function with validation and timeout."""
        func = self._functions.get(name)
        if not func:
            raise ValueError(f"Function '{name}' not registered.")

        # 1. Parameter Validation
        sig = inspect.signature(func)
        try:
            sig.bind(**kwargs)
        except TypeError as e:
            raise ValueError(f"Invalid arguments for function '{name}': {e}")

        # 2. Executing with Timeout
        logger.info(f"Executing function '{name}' with timeout {self.execution_timeout}s")
        start_time = time.time()

        try:
            if inspect.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(**kwargs), timeout=self.execution_timeout)
            else:
                # Run sync functions in thread to avoid blocking loop
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: func(**kwargs)
                )

            execution_time = time.time() - start_time
            logger.info(f"Function '{name}' executed successfully in {execution_time:.3f}s")
            return result

        except asyncio.TimeoutError:
            logger.error(f"Function '{name}' execution timed out after {self.execution_timeout}s")
            raise TimeoutError(f"Function '{name}' execution timed out")
        except Exception as e:
            logger.error(f"Error executing function '{name}': {e}")
            raise

    def get_registered_functions_metadata(self) -> dict[str, dict[str, Any]]:
        """Returns metadata for all registered functions."""
        metadata = {}
        for name, func in self._functions.items():
            sig = inspect.signature(func)
            parameters = {}
            for param_name, param in sig.parameters.items():
                parameters[param_name] = {
                    "kind": str(param.kind),
                    "default": (
                        str(param.default) if param.default != inspect.Parameter.empty else None
                    ),
                    "annotation": (
                        str(param.annotation)
                        if param.annotation != inspect.Parameter.empty
                        else None
                    ),
                }

            metadata[name] = {
                "name": name,
                "description": func.__doc__ or "No description provided.",
                "parameters": parameters,
            }
        return metadata
