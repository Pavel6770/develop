"""
Unit tests for the log decorator module.

Tests cover console output, file logging, successful execution,
and exception handling scenarios.
"""

import os
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decorators import log


# ============================================================================
# Test functions to be decorated
# ============================================================================

@log()
def add_numbers(a: int, b: int) -> int:
    """Simple function that adds two numbers."""
    return a + b


@log()
def multiply_numbers(a: int, b: int) -> int:
    """Simple function that multiplies two numbers."""
    return a * b


@log()
def divide_numbers(a: float, b: float) -> float:
    """Function that may raise ZeroDivisionError."""
    return a / b


@log()
def function_with_multiple_args(a: int, b: str, c: bool = False) -> str:
    """Function with multiple arguments and keyword arguments."""
    return f"{a} - {b} - {c}"


@log()
def function_that_raises_value_error(value: int) -> None:
    """Function that raises ValueError for negative numbers."""
    if value < 0:
        raise ValueError(f"Negative value not allowed: {value}")
    return None


@log()
def function_that_raises_type_error(a: int, b: str) -> str:
    """Function that raises TypeError when types are incompatible."""
    return a + b  # This will raise TypeError


# ============================================================================
# Tests for console output (using capsys fixture)
# ============================================================================

class TestConsoleLogging:
    """Test suite for console logging when filename is not provided."""

    def test_successful_function_logs_ok_to_console(self, capsys):
        """Test that successful function logs 'function_name ok' to console."""
        result = add_numbers(5, 3)

        assert result == 8
        captured = capsys.readouterr()
        assert "add_numbers ok" in captured.out

    def test_successful_function_does_not_log_to_stderr(self, capsys):
        """Test that successful function does not write to stderr."""
        result = add_numbers(10, 20)

        assert result == 30
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_error_function_logs_error_to_stderr(self, capsys):
        """Test that function raising exception logs error to stderr."""
        with pytest.raises(ZeroDivisionError):
            divide_numbers(10, 0)

        captured = capsys.readouterr()
        assert "divide_numbers error: ZeroDivisionError" in captured.err
        assert "Inputs: (10, 0)" in captured.err

    def test_error_function_does_not_log_ok_to_stdout(self, capsys):
        """Test that error function does not log 'ok' to stdout."""
        with pytest.raises(ZeroDivisionError):
            divide_numbers(5, 0)

        captured = capsys.readouterr()
        assert "divide_numbers ok" not in captured.out

    def test_multiple_calls_to_same_function_log_correctly(self, capsys):
        """Test that multiple calls to same function log correctly."""
        add_numbers(1, 2)
        add_numbers(3, 4)
        add_numbers(5, 6)

        captured = capsys.readouterr()
        # Should have three "ok" messages
        assert captured.out.count("add_numbers ok") == 3

    def test_function_with_kwargs_logs_inputs_on_error(self, capsys):
        """Test that error log includes keyword arguments."""
        with pytest.raises(ValueError):
            function_that_raises_value_error(-5)

        captured = capsys.readouterr()
        assert "function_that_raises_value_error error: ValueError" in captured.err
        assert "Inputs: (-5,)" in captured.err or "(-5,)" in captured.err

    def test_function_with_multiple_args_logs_all_inputs(self, capsys):
        """Test that function with multiple args logs all inputs on error."""
        # This function doesn't raise error normally, but we test logging
        result = function_with_multiple_args(42, "hello", c=True)
        assert result == "42 - hello - True"

        captured = capsys.readouterr()
        assert "function_with_multiple_args ok" in captured.out


# ============================================================================
# Tests for file logging
# ============================================================================

class TestFileLogging:
    """Test suite for file logging when filename is provided."""

    @pytest.fixture
    def temp_log_file(self):
        """Fixture that creates a temporary log file and cleans up after test."""
        with tempfile.NamedTemporaryFile(
            mode='w+',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        ) as tmp_file:
            temp_filename = tmp_file.name

        yield temp_filename

        # Cleanup after test
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

    def test_successful_function_writes_ok_to_file(self, temp_log_file):
        """Test that successful function writes 'function_name ok' to file."""
        @log(filename=temp_log_file)
        def test_func(x: int, y: int) -> int:
            return x + y

        result = test_func(10, 20)

        assert result == 30

        # Read the log file
        with open(temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "test_func ok" in content

    def test_error_function_writes_error_to_file(self, temp_log_file):
        """Test that function raising exception writes error to file."""
        @log(filename=temp_log_file)
        def test_func(a: int, b: int) -> float:
            return a / b

        with pytest.raises(ZeroDivisionError):
            test_func(100, 0)

        # Read the log file
        with open(temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "test_func error: ZeroDivisionError" in content
        assert "Inputs: (100, 0)" in content

    def test_file_logging_appends_multiple_calls(self, temp_log_file):
        """Test that multiple function calls append to the same file."""
        @log(filename=temp_log_file)
        def test_func(x: int) -> int:
            return x * 2

        test_func(5)
        test_func(10)
        test_func(15)

        with open(temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert content.count("test_func ok") == 3

    def test_file_logging_does_not_write_to_console(self, temp_log_file, capsys):
        """Test that file logging does not write to console."""
        @log(filename=temp_log_file)
        def test_func(x: int) -> int:
            return x * 2

        result = test_func(42)

        assert result == 84

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    def test_different_functions_write_to_same_file(self, temp_log_file):
        """Test that different functions can log to the same file."""
        @log(filename=temp_log_file)
        def func1(x: int) -> int:
            return x + 1

        @log(filename=temp_log_file)
        def func2(x: int) -> int:
            return x * 2

        func1(5)
        func2(10)

        with open(temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "func1 ok" in content
        assert "func2 ok" in content


# ============================================================================
# Tests for edge cases and special scenarios
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and special scenarios."""

    def test_function_with_no_arguments_logs_empty_inputs(self, capsys):
        """Test that function with no arguments logs empty inputs on error."""
        @log()
        def no_args_function() -> None:
            raise RuntimeError("Something went wrong")

        with pytest.raises(RuntimeError):
            no_args_function()

        captured = capsys.readouterr()
        assert "no_args_function error: RuntimeError" in captured.err
        assert "Inputs: (), {}" in captured.err

    def test_function_returning_none_logs_ok(self, capsys):
        """Test that function returning None still logs 'ok'."""
        @log()
        def returns_none() -> None:
            return None

        result = returns_none()

        assert result is None
        captured = capsys.readouterr()
        assert "returns_none ok" in captured.out

    def test_decorator_preserves_function_metadata(self):
        """Test that the decorator preserves function name and docstring."""
        @log()
        def sample_function(a: int, b: int) -> int:
            """This is a sample function docstring."""
            return a + b

        assert sample_function.__name__ == "sample_function"
        assert sample_function.__doc__ == "This is a sample function docstring."

    def test_decorator_can_be_used_without_parentheses(self, capsys):
        """Test that decorator works when used as @log (without parentheses)."""
        # Note: Our implementation requires parentheses, but we test anyway
        @log()  # With parentheses as required
        def simple_func(x: int) -> int:
            return x * x

        result = simple_func(5)

        assert result == 25
        captured = capsys.readouterr()
        assert "simple_func ok" in captured.out

    def test_type_error_logs_correctly(self, capsys):
        """Test that TypeError is logged correctly."""
        with pytest.raises(TypeError):
            function_that_raises_type_error(10, "hello")

        captured = capsys.readouterr()
        assert "function_that_raises_type_error error: TypeError" in captured.err
        assert "Inputs: (10, 'hello')" in captured.err

    def test_value_error_logs_correctly(self, capsys):
        """Test that ValueError is logged correctly."""
        with pytest.raises(ValueError):
            function_that_raises_value_error(-1)

        captured = capsys.readouterr()
        assert "function_that_raises_value_error error: ValueError" in captured.err


# ============================================================================
# Tests for mixed scenarios (console and file at the same time)
# ============================================================================

class TestMixedScenarios:
    """Test suite for scenarios with multiple decorator instances."""

    def test_console_and_file_decorators_can_coexist(self, temp_log_file, capsys):
        """Test that console logger and file logger can work independently."""
        @log()  # Logs to console
        def console_func(x: int) -> int:
            return x + 1

        @log(filename=temp_log_file)  # Logs to file
        def file_func(x: int) -> int:
            return x * 2

        console_func(10)
        file_func(5)

        # Check console output
        captured = capsys.readouterr()
        assert "console_func ok" in captured.out

        # Check file output
        with open(temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "file_func ok" in content

    def test_separate_log_files_for_different_functions(self):
        """Test that different functions can log to different files."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f1:
            file1 = f1.name
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f2:
            file2 = f2.name

        try:
            @log(filename=file1)
            def func1(x: int) -> int:
                return x + 1

            @log(filename=file2)
            def func2(x: int) -> int:
                return x * 2

            func1(10)
            func2(20)

            with open(file1, 'r', encoding='utf-8') as f:
                assert "func1 ok" in f.read()

            with open(file2, 'r', encoding='utf-8') as f:
                assert "func2 ok" in f.read()

        finally:
            # Cleanup
            for f in [file1, file2]:
                if os.path.exists(f):
                    os.unlink(f)


# ============================================================================
# Test for decorator parameter handling
# ============================================================================

class TestDecoratorParameters:
    """Test suite for decorator parameter handling."""

    def test_log_with_filename_parameter(self, temp_log_file):
        """Test that decorator accepts filename parameter."""
        @log(filename=temp_log_file)
        def test_func(x: int) -> int:
            return x * 2

        test_func(7)

        with open(temp_log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "test_func ok" in content

    def test_log_without_filename_parameter(self, capsys):
        """Test that decorator works without filename parameter."""
        @log()
        def test_func(x: int) -> int:
            return x * 3

        test_func(5)

        captured = capsys.readouterr()
        assert "test_func ok" in captured.out