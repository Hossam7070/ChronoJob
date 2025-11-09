# ChronoJob Dashboard - Quick Start Guide

Get your ChronoJob dashboard up and running in minutes!

## Prerequisites

Before you begin, ensure you have:
- **Node.js 18+** installed ([Download here](https://nodejs.org/))
- **ChronoJob backend** running on `http://localhost:8000`

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

That's it! You should now see the ChronoJob dashboard.

## First Steps

### Creating Your First Job

1. Click **"Create Job"** in the navigation bar
2. Fill in the job details:
   - **Job Name**: A unique identifier (e.g., `daily_sales_report`)
   - **Schedule**: Use a cron expression (e.g., `0 9 * * 1-5` for 9 AM weekdays)
   - **Data Source**: Choose API or File and provide the location
   - **Processing Script**: Write Python code to process your data
   - **Recipients**: Add email addresses to receive the results

3. Click **"Create Job"** to save

### Managing Jobs

From the Dashboard view, you can:
- **View all jobs** with their schedules and details
- **Click on a job** to see full configuration
- **Delete jobs** using the trash icon
- **Refresh** the list to see latest updates

## Cron Expression Examples

Need help with cron expressions? Here are some common patterns:

| Expression | Description |
|------------|-------------|
| `0 9 * * 1-5` | 9 AM, Monday through Friday |
| `30 14 * * *` | 2:30 PM every day |
| `0 */6 * * *` | Every 6 hours |
| `0 0 1 * *` | First day of every month at midnight |
| `0 0 * * 0` | Every Sunday at midnight |

## Python Script Guidelines

Your processing script should:
- Accept a DataFrame named `data` as input
- Return a DataFrame named `result` as output
- Use pandas operations for data manipulation

Example:
```python
# Filter and aggregate data
filtered = data[data['amount'] > 100]
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'count'
}).reset_index()
```

## Troubleshooting

### Dashboard won't load
- Ensure the backend is running on `http://localhost:8000`
- Check the browser console for errors
- Verify the proxy configuration in `vite.config.ts`

### Can't create jobs
- Verify all required fields are filled
- Check that the cron expression is valid
- Ensure the job name is unique
- Check that at least one email recipient is provided

### Jobs not appearing
- Click the refresh button
- Check the browser console for API errors
- Verify the backend is accessible

## Production Deployment

### Build for production:
```bash
npm run build
```

The optimized files will be in the `dist/` directory.

### Serve with a static file server:
```bash
npm run preview
```

Or use any static file server like nginx, Apache, or serve.

## Need Help?

- Check the main [README.md](./README.md) for detailed documentation
- Review the backend API documentation
- Check the browser console for error messages

## Next Steps

- Explore the dashboard features
- Create multiple jobs with different schedules
- Monitor job execution and results
- Customize the dashboard styling in `tailwind.config.js`

Happy scheduling! 🚀
