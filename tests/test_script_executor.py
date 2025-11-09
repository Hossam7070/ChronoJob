"""Tests for script executor module."""

import pytest
import pandas as pd
from app.executor.script_executor import (
    execute_script,
    ScriptExecutionError,
    ScriptTimeoutError,
    ScriptOutputError
)


def test_execute_simple_script():
    """Test executing a simple script that processes data."""
    input_df = pd.DataFrame({
        'value': [1, 2, 3, 4, 5]
    })
    
    script = """
result = data.copy()
result['doubled'] = result['value'] * 2
"""
    
    output_df = execute_script(script, input_df)
    
    assert isinstance(output_df, pd.DataFrame)
    assert 'doubled' in output_df.columns
    assert output_df['doubled'].tolist() == [2, 4, 6, 8, 10]


def test_execute_script_with_pandas_operations():
    """Test script with pandas operations."""
    input_df = pd.DataFrame({
        'category': ['A', 'B', 'A', 'B', 'A'],
        'amount': [10, 20, 30, 40, 50]
    })
    
    script = """
result = data.groupby('category')['amount'].sum().reset_index()
"""
    
    output_df = execute_script(script, input_df)
    
    assert isinstance(output_df, pd.DataFrame)
    assert len(output_df) == 2
    assert output_df['amount'].sum() == 150


def test_execute_script_with_numpy():
    """Test script using numpy operations."""
    input_df = pd.DataFrame({
        'values': [1.5, 2.7, 3.2, 4.8]
    })
    
    script = """
result = data.copy()
result['rounded'] = np.round(result['values'])
"""
    
    output_df = execute_script(script, input_df)
    
    assert isinstance(output_df, pd.DataFrame)
    assert 'rounded' in output_df.columns


def test_execute_script_modifies_data_variable():
    """Test script that modifies data variable instead of creating result."""
    input_df = pd.DataFrame({
        'x': [1, 2, 3]
    })
    
    script = """
data['y'] = data['x'] + 10
"""
    
    output_df = execute_script(script, input_df)
    
    assert isinstance(output_df, pd.DataFrame)
    assert 'y' in output_df.columns
    assert output_df['y'].tolist() == [11, 12, 13]


def test_execute_script_with_syntax_error():
    """Test error handling for script with syntax error."""
    input_df = pd.DataFrame({'a': [1, 2, 3]})
    
    script = """
result = data.copy(
"""  # Missing closing parenthesis
    
    with pytest.raises(ScriptExecutionError, match="Script execution failed"):
        execute_script(script, input_df)


def test_execute_script_with_runtime_error():
    """Test error handling for script with runtime error."""
    input_df = pd.DataFrame({'a': [1, 2, 3]})
    
    script = """
result = data['nonexistent_column']
"""
    
    with pytest.raises(ScriptExecutionError, match="Script execution failed"):
        execute_script(script, input_df)


def test_execute_script_with_invalid_output():
    """Test error handling when script doesn't return DataFrame."""
    input_df = pd.DataFrame({'a': [1, 2, 3]})
    
    script = """
result = "not a dataframe"
"""
    
    with pytest.raises(ScriptOutputError, match="must return a Pandas DataFrame"):
        execute_script(script, input_df)


def test_execute_script_with_timeout():
    """Test timeout enforcement for long-running scripts."""
    input_df = pd.DataFrame({'a': [1, 2, 3]})
    
    script = """
time.sleep(5)
result = data.copy()
"""
    
    with pytest.raises(ScriptTimeoutError, match="exceeded timeout"):
        execute_script(script, input_df, timeout=1)


def test_execute_empty_script():
    """Test error handling for empty script."""
    input_df = pd.DataFrame({'a': [1, 2, 3]})
    
    with pytest.raises(ScriptExecutionError, match="cannot be empty"):
        execute_script("", input_df)


def test_execute_script_with_invalid_input():
    """Test error handling for invalid input data."""
    with pytest.raises(ScriptExecutionError, match="must be a Pandas DataFrame"):
        execute_script("result = data", "not a dataframe")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
