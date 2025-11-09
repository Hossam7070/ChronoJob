# ChronoJob Dashboard

A modern, responsive React dashboard for managing the ChronoJob scheduled jobs service.

## Features

- **Job Dashboard**: View all scheduled jobs with real-time status
- **Job Creation**: Intuitive form for creating new scheduled jobs
- **Job Management**: View details, delete jobs, and monitor execution
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modern UI**: Built with Tailwind CSS for a clean, professional look

## Tech Stack

- **React 18** with TypeScript
- **React Router** for navigation
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons
- **Cronstrue** for human-readable cron expressions
- **Vite** for fast development and building

## Prerequisites

- Node.js 16+ and npm/yarn
- ChronoJob backend running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Development

Start the development server:
```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

The Vite dev server is configured to proxy API requests to `http://localhost:8000`

## Building for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.tsx          # Main layout with navigation
│   ├── pages/
│   │   ├── Dashboard.tsx       # Job management dashboard
│   │   └── CreateJob.tsx       # Job creation form
│   ├── services/
│   │   └── api.ts              # API client
│   ├── types/
│   │   └── job.ts              # TypeScript types
│   ├── App.tsx                 # Main app component
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
├── public/                     # Static assets
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
└── vite.config.ts              # Vite configuration
```

## Features Overview

### Dashboard View
- List all scheduled jobs
- View job details (schedule, data source, script, recipients)
- Delete jobs with confirmation
- Real-time status updates
- Human-readable cron expressions
- Last run timestamps

### Create Job View
- Job name and schedule configuration
- Data source selection (API or File)
- Python script editor with syntax highlighting
- Multiple email recipients
- Cron expression examples
- Form validation
- Success/error notifications

## API Integration

The dashboard communicates with the FastAPI backend through the following endpoints:

- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{job_name}` - Get job details
- `POST /api/jobs/create` - Create new job
- `DELETE /api/jobs/{job_name}` - Delete job

## Customization

### Styling
Modify `tailwind.config.js` to customize the theme:
```javascript
theme: {
  extend: {
    colors: {
      // Add custom colors
    },
  },
}
```

### API Base URL
Update the proxy configuration in `vite.config.ts` if your backend runs on a different port:
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:YOUR_PORT',
      changeOrigin: true,
    },
  },
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

[Your License Here]
