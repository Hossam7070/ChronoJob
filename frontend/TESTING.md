# ChronoJob Dashboard - Testing Guide

Guide for testing the ChronoJob dashboard application.

## Manual Testing

### Pre-Testing Setup

1. **Start the backend:**
   ```bash
   cd ..
   python -m uvicorn app.main:app --reload
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser:**
   Navigate to `http://localhost:3000`

### Test Cases

#### 1. Dashboard View

**Test: Load Dashboard**
- [ ] Dashboard loads without errors
- [ ] Navigation bar displays correctly
- [ ] "ChronoJob" logo is visible
- [ ] "Dashboard" and "Create Job" links work

**Test: Empty State**
- [ ] When no jobs exist, empty state displays
- [ ] Empty state shows clock icon
- [ ] Message says "No jobs"
- [ ] "Create Job" link is present

**Test: Job List**
- [ ] All jobs display in cards
- [ ] Job names are visible
- [ ] Cron schedules show human-readable format
- [ ] Data source information displays
- [ ] Recipient count shows correctly
- [ ] Last run timestamp displays

**Test: Statistics Cards**
- [ ] Total Jobs count is correct
- [ ] Jobs Executed count is accurate
- [ ] Total Recipients sum is correct
- [ ] Icons display properly

**Test: Job Selection**
- [ ] Clicking a job card selects it
- [ ] Selected card has blue ring
- [ ] Details panel updates
- [ ] All job details display correctly

**Test: Refresh**
- [ ] Refresh button works
- [ ] Loading indicator shows
- [ ] Job list updates

**Test: Delete Job**
- [ ] Trash icon is visible on each card
- [ ] Clicking trash shows confirmation dialog
- [ ] Dialog shows correct job name
- [ ] Cancel button closes dialog
- [ ] Delete button removes job
- [ ] Job disappears from list
- [ ] Success feedback is shown

#### 2. Create Job View

**Test: Form Display**
- [ ] All form sections display
- [ ] Required fields marked with *
- [ ] Input fields are accessible
- [ ] Placeholder text is helpful

**Test: Job Name**
- [ ] Can enter job name
- [ ] Validation prevents empty name
- [ ] Long names are handled

**Test: Schedule**
- [ ] Can enter cron expression
- [ ] Example schedules display
- [ ] Clicking example fills field
- [ ] Invalid cron shows error

**Test: Data Source - API**
- [ ] Can select API radio button
- [ ] URL field appears
- [ ] Can enter API URL
- [ ] Validation works

**Test: Data Source - File**
- [ ] Can select File radio button
- [ ] File path field appears
- [ ] File type options display
- [ ] Can select CSV or JSON
- [ ] Can enter file path

**Test: Processing Script**
- [ ] Text area displays
- [ ] Can enter Python code
- [ ] Monospace font is used
- [ ] Placeholder example shows
- [ ] Multi-line input works

**Test: Email Recipients**
- [ ] First email field displays
- [ ] Can enter email address
- [ ] Email validation works
- [ ] "Add Email" button works
- [ ] Multiple emails can be added
- [ ] Remove button (X) works
- [ ] Cannot remove last email

**Test: Form Submission**
- [ ] Submit button is enabled when valid
- [ ] Loading state shows during submission
- [ ] Success message displays
- [ ] Redirects to dashboard
- [ ] New job appears in list

**Test: Form Validation**
- [ ] Empty required fields show error
- [ ] Invalid email shows error
- [ ] Invalid cron shows error
- [ ] Error messages are clear

**Test: Cancel**
- [ ] Cancel button works
- [ ] Returns to dashboard
- [ ] No job is created

#### 3. Navigation

**Test: Route Changes**
- [ ] Dashboard link works
- [ ] Create Job link works
- [ ] Browser back button works
- [ ] Direct URL access works
- [ ] 404 redirects properly

#### 4. Responsive Design

**Test: Desktop (1920x1080)**
- [ ] Layout is proper
- [ ] Two-column grid works
- [ ] All content is visible
- [ ] No horizontal scroll

**Test: Tablet (768x1024)**
- [ ] Layout adapts
- [ ] Navigation is accessible
- [ ] Forms are usable
- [ ] Cards stack properly

**Test: Mobile (375x667)**
- [ ] Mobile layout works
- [ ] Navigation is accessible
- [ ] Forms are usable
- [ ] Text is readable
- [ ] Buttons are tappable

#### 5. Error Handling

**Test: Network Errors**
- [ ] Backend offline shows error
- [ ] Error message is clear
- [ ] Can retry operation
- [ ] UI remains functional

**Test: API Errors**
- [ ] 400 errors show message
- [ ] 404 errors handled
- [ ] 500 errors show message
- [ ] Error can be dismissed

**Test: Invalid Data**
- [ ] Malformed responses handled
- [ ] Missing data handled gracefully
- [ ] Type errors prevented

#### 6. Browser Compatibility

**Test: Chrome**
- [ ] All features work
- [ ] Styling is correct
- [ ] No console errors

**Test: Firefox**
- [ ] All features work
- [ ] Styling is correct
- [ ] No console errors

**Test: Safari**
- [ ] All features work
- [ ] Styling is correct
- [ ] No console errors

**Test: Edge**
- [ ] All features work
- [ ] Styling is correct
- [ ] No console errors

### Performance Testing

**Test: Load Time**
- [ ] Initial load < 3 seconds
- [ ] Dashboard loads quickly
- [ ] No lag when switching views

**Test: Large Data Sets**
- [ ] 50+ jobs display properly
- [ ] Scrolling is smooth
- [ ] No memory leaks
- [ ] Performance remains good

### Accessibility Testing

**Test: Keyboard Navigation**
- [ ] Tab order is logical
- [ ] All interactive elements accessible
- [ ] Enter key submits forms
- [ ] Escape closes dialogs

**Test: Screen Readers**
- [ ] Labels are present
- [ ] ARIA attributes used
- [ ] Error messages announced
- [ ] Status updates announced

**Test: Color Contrast**
- [ ] Text is readable
- [ ] Meets WCAG standards
- [ ] Color is not sole indicator

## Automated Testing Setup

### Unit Tests (Future Enhancement)

Install testing dependencies:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

Create `vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
```

### Example Test

Create `src/components/__tests__/JobCard.test.tsx`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import JobCard from '../JobCard'

describe('JobCard', () => {
  const mockJob = {
    job_name: 'test_job',
    schedule_time: '0 9 * * 1-5',
    data_source: {
      source_type: 'api',
      location: 'https://api.example.com/data',
    },
    processing_script: 'result = data',
    consumer_emails: ['test@example.com'],
    created_at: '2024-01-01T00:00:00',
  }

  it('renders job name', () => {
    render(
      <JobCard
        job={mockJob}
        isSelected={false}
        onClick={() => {}}
        onDelete={() => {}}
      />
    )
    expect(screen.getByText('test_job')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(
      <JobCard
        job={mockJob}
        isSelected={false}
        onClick={onClick}
        onDelete={() => {}}
      />
    )
    fireEvent.click(screen.getByText('test_job'))
    expect(onClick).toHaveBeenCalled()
  })
})
```

### E2E Tests (Future Enhancement)

Install Playwright:
```bash
npm install -D @playwright/test
```

Create `e2e/dashboard.spec.ts`:
```typescript
import { test, expect } from '@playwright/test'

test('dashboard loads and displays jobs', async ({ page }) => {
  await page.goto('http://localhost:3000')
  await expect(page.locator('h1')).toContainText('Job Dashboard')
})

test('can create a new job', async ({ page }) => {
  await page.goto('http://localhost:3000/create')
  await page.fill('#job_name', 'test_job')
  await page.fill('#schedule_time', '0 9 * * *')
  await page.fill('#location', 'https://api.example.com/data')
  await page.fill('#processing_script', 'result = data')
  await page.fill('input[type="email"]', 'test@example.com')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL(/.*dashboard/)
})
```

## Testing Checklist

### Before Each Release

- [ ] Run all manual test cases
- [ ] Test on multiple browsers
- [ ] Test responsive design
- [ ] Check console for errors
- [ ] Verify API integration
- [ ] Test error scenarios
- [ ] Check accessibility
- [ ] Review performance
- [ ] Test with real data
- [ ] Verify documentation

### Regression Testing

When making changes:
- [ ] Test affected features
- [ ] Test related features
- [ ] Verify no new bugs
- [ ] Check performance impact

## Bug Reporting

When reporting bugs, include:
1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Browser and version**
5. **Screenshots/videos**
6. **Console errors**
7. **Network requests**

## Test Data

### Sample Jobs

**Simple API Job:**
```json
{
  "job_name": "test_api_job",
  "schedule_time": "0 9 * * *",
  "data_source": {
    "source_type": "api",
    "location": "https://jsonplaceholder.typicode.com/users"
  },
  "processing_script": "result = data.head(5)",
  "consumer_emails": ["test@example.com"]
}
```

**File Job:**
```json
{
  "job_name": "test_file_job",
  "schedule_time": "30 14 * * *",
  "data_source": {
    "source_type": "file",
    "location": "./data/test.csv",
    "file_type": "csv"
  },
  "processing_script": "result = data[data['amount'] > 100]",
  "consumer_emails": ["user1@example.com", "user2@example.com"]
}
```

## Continuous Testing

### CI/CD Integration

Add to `.github/workflows/test.yml`:
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - run: npm run test
```

## Performance Benchmarks

Target metrics:
- **Initial Load**: < 3 seconds
- **Time to Interactive**: < 5 seconds
- **Bundle Size**: < 500KB (gzipped)
- **Lighthouse Score**: > 90

## Security Testing

- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Input validation
- [ ] Output sanitization
- [ ] Secure headers
- [ ] HTTPS enforcement

---

**Happy Testing!** ✅
