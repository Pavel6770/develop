"""
Module for custom decorators.

This module provides a `log` decorator for logging function calls,
results, and errors to a file or console.
"""

import functools
import sys
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable:
    """
    Decorator that logs function result or error.

    Args:
        filename: Optional file path for logging. If not provided,
                  logs are written to console.

    Returns:
        Decorated function with logging functionality.

    Example:
        @log(filename="mylog.txt")
        def my_function(x, y):
            return x + y

        my_function(1, 2)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Determine where to write logs
            output_file = None
            if filename:
                output_file = open(filename, 'a', encoding='utf-8')

            try:
                result = func(*args, **kwargs)
                # Log successful execution
                log_message = f"{func.__name__} ok\n"
                if output_file:
                    output_file.write(log_message)
                else:
                    sys.stdout.write(log_message)
                return result

            except Exception as e:
                # Log error with function name, error type, and inputs
                error_type = type(e).__name__
                log_message = (
                    f"{func.__name__} error: {error_type}. "
                    f"Inputs: {args}, {kwargs}\n"
                )
                if output_file:
                    output_file.write(log_message)
                else:
                    sys.stderr.write(log_message)
                raise

            finally:
                if output_file:
                    output_file.close()

        return wrapper
    return decorator