# Script Debugger Module

## Overview

The Script Debugger is a Jupyter-like code editor that allows users to write, test, and debug Python data processing scripts with live feedback before using them in scheduled jobs.

## Features

### 1. Interactive Script Editor
- **Code Editor**: Write Python scripts with syntax highlighting
- **Live Testing**: Execute scripts on sample data files
- **Error Logging**: View detailed error messages and tracebacks
- **Output Preview**: See the first 10 rows of processed data

### 2. Test Data Upload
- Upload CSV or JSON files for testing
- Files are stored in `data/uploads/test/`
- Reuse test files across multiple script tests

### 3. Script Management
- **Save Scripts**: Store scripts with names and descriptions
- **Load Scripts**: Quick access to saved scripts
- **Script Library**: View all saved scripts in the sidebar
- **Reusable**: Use saved scripts in job creation

### 4. Detailed Test Results
When you run a test, you get:
- ✅ Success/failure status
- 📊 Input and output data shapes
- 📋 Column names and data types
- 👁️ Preview of output data (first 10 rows)
- ❌ Error messages with full tracebacks

## How to Use

### Step 1: Upload Test Data
1. Navigate to **Script Debugger** in the navigation menu
2. Click "Choose File" under Test Data
3. Select a CSV or JSON file
4. File is automatically uploaded

### Step 2: Write Your Script
Write your Python script in the editor. Your script should:
- Use `data` as the input DataFrame (automatically provided)
- Assign the result to a variable named `result`
- Use available libraries: pandas (pd), numpy (np), datetime

Example:
```python
# Filter and aggregate data
filtered = data[data['amount'] > 100]
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'count'
}).reset_index()
```

### Step 3: Run Test
1. Click the "Run Test" button
2. View the results below the editor
3. If there are errors, check the error message and traceback
4. Fix the script and test again

### Step 4: Save Script
Once your script works correctly:
1. Enter a script name (e.g., "sales_aggregator")
2. Optionally add a description
3. Click "Save Script"
4. Script is now available in the saved scripts library

### Step 5: Use in Jobs
When creating or editing a job:
1. In the Processing Script section, click "Load Saved Script"
2. Select your saved script from the dropdown
3. The script content is automatically loaded
4. Continue with job creation

## API Endpoints

### Script Management
- `POST /api/scripts/create` - Create a new script
- `GET /api/scripts` - List all scripts
- `GET /api/scripts/{script_name}` - Get a specific script
- `PUT /api/scripts/{script_name}` - Update a script
- `DELETE /api/scripts/{script_name}` - Delete a script

### Testing
- `POST /api/scripts/test` - Test a script with sample data
- `POST /api/scripts/upload-test-file` - Upload a test data file

## Script Execution Environment

### Available Libraries
- **pandas** (as `pd`): Data manipulation
- **numpy** (as `np`): Numerical operations
- **datetime**: Date and time operations
- **timedelta**: Time delta operations

### Built-in Functions
abs, all, any, bool, dict, enumerate, float, int, len, list, max, min, range, round, set, sorted, str, sum, tuple, zip

### Security
Scripts run in a restricted environment with:
- Limited built-in functions
- No file system access
- No network access
- Execution timeout (configurable)

## Data Storage

### Scripts
- Stored in: `data/scripts.json`
- Format: JSON array of script configurations
- Fields: script_name, description, script_content, created_at, updated_at

### Test Files
- Stored in: `data/uploads/test/`
- Supported formats: CSV, JSON
- Automatically cleaned up (optional)

## Tips

1. **Start Simple**: Test with a small sample file first
2. **Check Columns**: Verify your test data has the expected columns
3. **Use Print Statements**: While not visible in output, they help during development
4. **Save Often**: Save working versions of your scripts
5. **Descriptive Names**: Use clear script names and descriptions
6. **Test Edge Cases**: Try different data scenarios

## Troubleshooting

### Common Errors

**"Script must return a Pandas DataFrame"**
- Make sure you assign your result to a variable named `result`
- Verify the result is a DataFrame, not a Series or other type

**"KeyError: 'column_name'"**
- Check that your test data has the expected columns
- Use `data.columns` to see available columns

**"Script execution exceeded timeout"**
- Your script is taking too long
- Optimize your code or reduce test data size
- Default timeout is configurable in backend settings

**"Failed to load test data"**
- Verify file format (CSV or JSON)
- Check file is not corrupted
- Ensure file has proper structure

## Future Enhancements

- [ ] Syntax highlighting in code editor
- [ ] Auto-completion for pandas/numpy functions
- [ ] Multiple test files per script
- [ ] Script versioning
- [ ] Export test results
- [ ] Collaborative script sharing
- [ ] Script templates library
