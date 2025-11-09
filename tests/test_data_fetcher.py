"""Tests for data fetcher module."""

import pytest
import pandas as pd
from pathlib import Path
from app.executor.data_fetcher import fetch_data, fetch_from_file, DataFetchError
from app.models.job import DataSource


def test_fetch_from_csv_file():
    """Test fetching data from a CSV file."""
    # Create test CSV file
    test_file = Path("data/test_data.csv")
    test_file.parent.mkdir(exist_ok=True)
    
    test_df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['New York', 'London', 'Paris']
    })
    test_df.to_csv(test_file, index=False)
    
    try:
        # Test fetching
        result_df = fetch_from_file(str(test_file), 'csv')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        assert list(result_df.columns) == ['name', 'age', 'city']
        assert result_df['name'].tolist() == ['Alice', 'Bob', 'Charlie']
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_fetch_from_json_file():
    """Test fetching data from a JSON file."""
    # Create test JSON file
    test_file = Path("data/test_data.json")
    test_file.parent.mkdir(exist_ok=True)
    
    test_df = pd.DataFrame({
        'product': ['Widget', 'Gadget'],
        'price': [10.99, 25.50],
        'stock': [100, 50]
    })
    test_df.to_json(test_file, orient='records')
    
    try:
        # Test fetching
        result_df = fetch_from_file(str(test_file), 'json')
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        assert 'product' in result_df.columns
        assert 'price' in result_df.columns
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_fetch_from_nonexistent_file():
    """Test error handling for nonexistent file."""
    with pytest.raises(DataFetchError, match="File not found"):
        fetch_from_file("nonexistent_file.csv", "csv")


@pytest.mark.asyncio
async def test_fetch_data_with_file_source():
    """Test fetch_data function with file source."""
    # Create test CSV file
    test_file = Path("data/test_fetch_data.csv")
    test_file.parent.mkdir(exist_ok=True)
    
    test_df = pd.DataFrame({
        'id': [1, 2, 3],
        'value': [100, 200, 300]
    })
    test_df.to_csv(test_file, index=False)
    
    try:
        data_source = DataSource(
            source_type="file",
            location=str(test_file),
            file_type="csv"
        )
        
        result_df = await fetch_data(data_source)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        assert list(result_df.columns) == ['id', 'value']
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
