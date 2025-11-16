# Script Debugger - Quick Start Guide

## What is the Script Debugger?

The Script Debugger is a Jupyter-like interactive environment where you can write, test, and debug Python data processing scripts before using them in your scheduled jobs. Think of it as a playground for your data transformation logic.

## Quick Start (5 minutes)

### 1. Start the Application

**Backend:**
```bash
./start_backend.sh
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Navigate to Script Debugger

Open your browser and go to: `http://localhost:5173/script-debugger`

### 3. Upload Test Data

We've included a sample file for you to try:
- Click "Choose File" under Test Data
- Navigate to `data/uploads/test/sample_sales.csv`
- The file will upload automatically

### 4. Write Your First Script

Try this simple example:

```python
# Filter sales over $100
filtered = data[data['amount'] > 100]

# Group by category and sum
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'sum'
}).reset_index()
```

### 5. Run the Test

Click the "Run Test" button. You should see:
- ✅ Success message
- Input shape: 10 × 4
- Output shape: 2 × 3
- A preview table showing aggregated results

### 6. Save Your Script

1. Enter a name: `sales_filter_aggregate`
2. Add description: `Filters sales over $100 and aggregates by category`
3. Click "Save Script"

### 7. Use in a Job

1. Go to "Create Job"
2. In the Processing Script section, click "Load Saved Script"
3. Select your saved script
4. Continue creating your job as normal

## Example Scripts

### Example 1: Basic Filtering
```python
# Keep only high-value transactions
result = data[data['amount'] > 100]
```

### Example 2: Column Selection
```python
# Select specific columns
result = data[['category', 'amount', 'date']]
```

### Example 3: Aggregation
```python
# Group by category and calculate statistics
result = data.groupby('category').agg({
    'amount': ['sum', 'mean', 'count'],
    'quantity': 'sum'
}).reset_index()

# Flatten column names
result.columns = ['category', 'total_amount', 'avg_amount', 'count', 'total_quantity']
```

### Example 4: Date Filtering
```python
from datetime import datetime, timedelta

# Convert date column to datetime
data['date'] = pd.to_datetime(data['date'])

# Filter last 7 days
cutoff_date = datetime.now() - timedelta(days=7)
result = data[data['date'] >= cutoff_date]
```

### Example 5: Adding Calculated Columns
```python
# Add a total price column
data['total_price'] = data['amount'] * data['quantity']

# Add a category flag
data['is_electronics'] = data['category'] == 'Electronics'

result = data
```

### Example 6: Sorting and Top N
```python
# Get top 5 highest amounts
result = data.nlargest(5, 'amount')
```

### Example 7: Pivot Table
```python
# Create a pivot table
result = data.pivot_table(
    values='amount',
    index='category',
    aggfunc='sum'
).reset_index()
```

## Common Patterns

### Pattern 1: Filter → Transform → Aggregate
```python
# Step 1: Filter
filtered = data[data['amount'] > 50]

# Step 2: Transform
filtered['revenue'] = filtered['amount'] * filtered['quantity']

# Step 3: Aggregate
result = filtered.groupby('category')['revenue'].sum().reset_index()
```

### Pattern 2: Multiple Conditions
```python
# Combine multiple filters
result = data[
    (data['amount'] > 100) & 
    (data['category'] == 'Electronics') &
    (data['quantity'] > 1)
]
```

### Pattern 3: Conditional Column
```python
# Add column based on condition
data['price_tier'] = data['amount'].apply(
    lambda x: 'High' if x > 150 else 'Medium' if x > 75 else 'Low'
)
result = data
```

## Debugging Tips

### Tip 1: Check Your Data First
```python
# See what columns you have
print(data.columns)

# See data types
print(data.dtypes)

# See first few rows
print(data.head())

# Your actual processing
result = data[data['amount'] > 100]
```

### Tip 2: Handle Missing Values
```python
# Drop rows with missing values
cleaned = data.dropna()

# Or fill with defaults
cleaned = data.fillna(0)

result = cleaned
```

### Tip 3: Type Conversion
```python
# Convert string to number
data['amount'] = pd.to_numeric(data['amount'], errors='coerce')

# Convert to datetime
data['date'] = pd.to_datetime(data['date'])

result = data
```

### Tip 4: Test with Small Data
Start with a small sample to test your logic:
```python
# Test with first 100 rows
sample = data.head(100)

# Your processing logic
filtered = sample[sample['amount'] > 100]
result = filtered.groupby('category')['amount'].sum().reset_index()
```

## Error Messages Explained

### "Script must return a Pandas DataFrame"
**Problem:** You forgot to assign the result or assigned the wrong type.

**Solution:**
```python
# ❌ Wrong - no result variable
data[data['amount'] > 100]

# ✅ Correct
result = data[data['amount'] > 100]
```

### "KeyError: 'column_name'"
**Problem:** The column doesn't exist in your data.

**Solution:**
```python
# Check available columns first
print(data.columns)

# Use correct column name
result = data[data['actual_column_name'] > 100]
```

### "Script execution exceeded timeout"
**Problem:** Your script is taking too long.

**Solution:**
- Simplify your logic
- Use vectorized operations instead of loops
- Test with smaller data first

### "TypeError: unsupported operand type"
**Problem:** You're trying to perform operations on incompatible types.

**Solution:**
```python
# Convert types first
data['amount'] = pd.to_numeric(data['amount'])
result = data[data['amount'] > 100]
```

## Best Practices

1. **Always assign to `result`**: This is what gets returned
2. **Test incrementally**: Build your script step by step
3. **Use descriptive names**: When saving scripts, use clear names
4. **Add comments**: Help your future self understand the logic
5. **Handle edge cases**: Consider empty data, missing values, etc.
6. **Keep it simple**: Complex logic is harder to debug
7. **Save working versions**: Save scripts that work before modifying

## Next Steps

1. ✅ Try the quick start example
2. ✅ Experiment with the example scripts
3. ✅ Create your own test data file
4. ✅ Write a script for your use case
5. ✅ Save and use it in a job

## Need Help?

- Check the error message and traceback
- Review the example scripts above
- Verify your test data format
- Start with simpler logic and build up
- Check pandas documentation for specific functions

Happy scripting! 🚀
