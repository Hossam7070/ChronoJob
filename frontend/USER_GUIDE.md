# ChronoJob Dashboard - User Guide

Complete guide to using the ChronoJob dashboard for managing scheduled data processing jobs.

## Table of Contents

1. [Overview](#overview)
2. [Dashboard View](#dashboard-view)
3. [Creating Jobs](#creating-jobs)
4. [Managing Jobs](#managing-jobs)
5. [Understanding Cron Expressions](#understanding-cron-expressions)
6. [Writing Processing Scripts](#writing-processing-scripts)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

ChronoJob Dashboard is a web-based interface for managing scheduled data processing jobs. It allows you to:
- Create automated jobs that run on a schedule
- Fetch data from APIs or files
- Process data using custom Python scripts
- Email results to specified recipients

## Dashboard View

The Dashboard is your central hub for monitoring all scheduled jobs.

### Key Features

**Statistics Cards**
- **Total Jobs**: Number of scheduled jobs
- **Jobs Executed**: Jobs that have run at least once
- **Total Recipients**: Sum of all email recipients across jobs

**Job List**
- View all jobs with key information
- Click any job to see full details
- Delete jobs with confirmation dialog
- Refresh to see latest updates

**Job Details Panel**
- Full job configuration
- Schedule information (human-readable and cron format)
- Data source details
- Complete processing script
- List of email recipients
- Creation and last run timestamps

### Navigation

- **Dashboard**: View and manage existing jobs
- **Create Job**: Create a new scheduled job

## Creating Jobs

### Step 1: Basic Information

**Job Name**
- Must be unique across all jobs
- Use descriptive names (e.g., `daily_sales_report`, `weekly_inventory_check`)
- Alphanumeric characters and underscores recommended
- Maximum 100 characters

**Schedule (Cron Expression)**
- Defines when the job runs
- Use standard cron format: `minute hour day month weekday`
- Click example schedules to auto-fill
- See [Understanding Cron Expressions](#understanding-cron-expressions) for details

### Step 2: Data Source

**Source Type**

Choose between two options:

1. **External API**
   - Fetches data from a REST API endpoint
   - Provide the full URL (e.g., `https://api.example.com/data`)
   - API should return JSON data

2. **Internal File**
   - Reads data from a local file
   - Provide the file path (e.g., `./data/input.csv`)
   - Choose file type: CSV or JSON

### Step 3: Processing Script

Write Python code to process your data:

**Requirements:**
- Script receives a pandas DataFrame named `data`
- Script must create a DataFrame named `result`
- Use pandas operations for data manipulation

**Example Scripts:**

*Filter and aggregate:*
```python
# Filter records above threshold
filtered = data[data['amount'] > 100]

# Group and aggregate
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'count'
}).reset_index()
```

*Calculate metrics:*
```python
# Add calculated columns
data['profit_margin'] = (data['revenue'] - data['cost']) / data['revenue']

# Sort and select top records
result = data.nlargest(10, 'profit_margin')
```

*Data transformation:*
```python
# Pivot data
result = data.pivot_table(
    values='sales',
    index='product',
    columns='region',
    aggfunc='sum'
).reset_index()
```

### Step 4: Email Recipients

**Adding Recipients**
- Enter valid email addresses
- Click "Add Email" to add more recipients
- Remove recipients using the X button
- At least one recipient is required

**Tips:**
- Use distribution lists for multiple recipients
- Verify email addresses are correct
- Recipients will receive processed data as CSV attachment

### Step 5: Submit

- Review all information
- Click "Create Job" to save
- Success message confirms creation
- Automatic redirect to Dashboard

## Managing Jobs

### Viewing Job Details

1. Navigate to Dashboard
2. Click on any job card
3. Details panel shows full configuration
4. Review schedule, data source, script, and recipients

### Deleting Jobs

1. Click the trash icon on a job card
2. Confirm deletion in the dialog
3. Job is removed from scheduler and storage
4. Action cannot be undone

### Refreshing Job List

- Click the "Refresh" button in the header
- Updates job list with latest data
- Shows current last run timestamps

## Understanding Cron Expressions

Cron expressions define when jobs run. Format: `minute hour day month weekday`

### Fields

| Field | Values | Special Characters |
|-------|--------|-------------------|
| Minute | 0-59 | * , - / |
| Hour | 0-23 | * , - / |
| Day | 1-31 | * , - / ? |
| Month | 1-12 | * , - / |
| Weekday | 0-6 (Sun-Sat) | * , - / ? |

### Special Characters

- `*` - Any value (every)
- `,` - List of values
- `-` - Range of values
- `/` - Step values

### Common Examples

| Expression | Description | Use Case |
|------------|-------------|----------|
| `0 9 * * 1-5` | 9 AM, Monday-Friday | Daily business reports |
| `30 14 * * *` | 2:30 PM daily | Afternoon updates |
| `0 */6 * * *` | Every 6 hours | Regular monitoring |
| `0 0 1 * *` | 1st of month, midnight | Monthly reports |
| `0 0 * * 0` | Sunday midnight | Weekly summaries |
| `*/15 * * * *` | Every 15 minutes | Frequent checks |
| `0 8,12,17 * * 1-5` | 8 AM, noon, 5 PM weekdays | Multiple daily runs |

### Testing Cron Expressions

Use online tools like [crontab.guru](https://crontab.guru/) to validate and understand cron expressions.

## Writing Processing Scripts

### Available Libraries

Your scripts have access to:
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- Standard Python libraries

### Input Data

The `data` variable contains:
- **From API**: JSON response converted to DataFrame
- **From CSV**: Parsed CSV file
- **From JSON**: Parsed JSON file

### Output Requirements

Create a `result` DataFrame with:
- Processed/filtered/aggregated data
- Appropriate column names
- Clean data types

### Best Practices

**1. Data Validation**
```python
# Check for required columns
required_cols = ['date', 'amount', 'category']
if not all(col in data.columns for col in required_cols):
    raise ValueError("Missing required columns")

# Handle missing values
data = data.dropna(subset=['amount'])
```

**2. Error Handling**
```python
try:
    # Your processing logic
    result = data.groupby('category')['amount'].sum().reset_index()
except Exception as e:
    # Fallback: return original data
    result = data
```

**3. Performance**
```python
# Use vectorized operations
data['total'] = data['price'] * data['quantity']

# Avoid loops when possible
# Instead of:
# for i, row in data.iterrows():
#     data.at[i, 'total'] = row['price'] * row['quantity']
```

**4. Data Quality**
```python
# Remove duplicates
data = data.drop_duplicates()

# Standardize formats
data['date'] = pd.to_datetime(data['date'])
data['email'] = data['email'].str.lower().str.strip()
```

## Best Practices

### Job Naming
- Use descriptive, meaningful names
- Include frequency in name (e.g., `daily_`, `weekly_`)
- Use consistent naming conventions
- Avoid special characters

### Scheduling
- Consider timezone (server timezone applies)
- Avoid overlapping job schedules
- Schedule resource-intensive jobs during off-peak hours
- Test with less frequent schedules first

### Data Sources
- Verify API endpoints are accessible
- Check file paths are correct
- Ensure data format is consistent
- Handle API rate limits

### Scripts
- Keep scripts simple and focused
- Test scripts with sample data first
- Add comments for complex logic
- Handle edge cases (empty data, missing columns)

### Recipients
- Use distribution lists for teams
- Verify email addresses
- Consider email volume
- Document who receives what data

## Troubleshooting

### Job Not Running

**Check:**
- Cron expression is valid
- Job appears in Dashboard
- Backend scheduler is running
- Server time matches expected schedule

**Solutions:**
- Verify cron expression with online tools
- Check backend logs for errors
- Restart backend service

### Data Fetch Errors

**API Issues:**
- Verify URL is accessible
- Check API authentication if required
- Confirm API returns valid JSON
- Check for rate limiting

**File Issues:**
- Verify file path is correct
- Ensure file exists and is readable
- Check file format matches specified type
- Verify file permissions

### Script Errors

**Common Issues:**
- Missing `result` variable
- Incorrect DataFrame operations
- Missing required columns
- Type errors

**Debugging:**
- Test script with sample data locally
- Add print statements (visible in logs)
- Check backend logs for error messages
- Simplify script to isolate issue

### Email Delivery

**Check:**
- Email addresses are valid
- SMTP configuration is correct
- Email service is running
- Check spam folders

### Dashboard Issues

**Can't Load Jobs:**
- Verify backend is running
- Check browser console for errors
- Refresh the page
- Clear browser cache

**Can't Create Jobs:**
- Verify all required fields
- Check for duplicate job names
- Validate cron expression
- Ensure at least one recipient

## Advanced Tips

### Complex Schedules

For complex scheduling needs:
- Create multiple jobs with different schedules
- Use cron expressions with multiple time points
- Consider job dependencies (manual coordination)

### Data Processing

For advanced processing:
- Chain multiple operations
- Use pandas merge/join for multiple data sources
- Apply custom functions with `.apply()`
- Use groupby for aggregations

### Monitoring

Best practices for monitoring:
- Check Dashboard regularly
- Review last run timestamps
- Monitor email deliveries
- Check backend logs for errors

### Performance

Optimize job performance:
- Limit data volume when possible
- Use efficient pandas operations
- Avoid unnecessary computations
- Consider data sampling for testing

## Getting Help

If you encounter issues:
1. Check this guide
2. Review error messages in browser console
3. Check backend logs
4. Verify configuration settings
5. Test with simpler job configurations

---

**Happy Scheduling!** 🎯
