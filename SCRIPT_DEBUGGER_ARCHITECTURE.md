# Script Debugger - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React + TypeScript)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Script     │    │  Create Job  │    │   Edit Job   │
│  Debugger    │    │     Page     │    │     Page     │
│    Page      │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        │                     └──────────┬──────────┘
        │                                │
        │                                │ Load Saved Scripts
        │                                │
        ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API SERVICE LAYER                          │
│                    (frontend/src/services/api.ts)               │
│                                                                  │
│  ┌──────────────┐                    ┌──────────────┐          │
│  │  scriptsApi  │                    │   jobsApi    │          │
│  └──────────────┘                    └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                          │
│                        (FastAPI)                                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API ROUTERS                                  │  │
│  │                                                            │  │
│  │  ┌──────────────┐              ┌──────────────┐          │  │
│  │  │   /scripts   │              │    /jobs     │          │  │
│  │  │              │              │              │          │  │
│  │  │ • create     │              │ • create     │          │  │
│  │  │ • update     │              │ • update     │          │  │
│  │  │ • list       │              │ • list       │          │  │
│  │  │ • get        │              │ • get        │          │  │
│  │  │ • delete     │              │ • delete     │          │  │
│  │  │ • test       │◄─────────────┤ • test       │          │  │
│  │  │ • upload     │              │ • upload     │          │  │
│  │  └──────────────┘              └──────────────┘          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Script     │    │    Script    │    │    Data      │
│   Storage    │    │   Executor   │    │   Fetcher    │
│              │    │              │    │              │
│ • save       │    │ • execute    │    │ • fetch      │
│ • load       │    │ • validate   │    │ • load       │
│ • get        │    │ • timeout    │    │              │
│ • delete     │    │ • sandbox    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA PERSISTENCE                           │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   scripts    │    │     jobs     │    │   uploads    │     │
│  │   .json      │    │    .json     │    │   /test/     │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Flow

### 1. Script Development Flow

```
User → Script Debugger Page
  │
  ├─→ Upload Test File
  │     │
  │     └─→ POST /api/scripts/upload-test-file
  │           │
  │           └─→ Save to data/uploads/test/
  │
  ├─→ Write Script in Editor
  │
  ├─→ Click "Run Test"
  │     │
  │     └─→ POST /api/scripts/test
  │           │
  │           ├─→ Load Test Data (Data Fetcher)
  │           │
  │           ├─→ Execute Script (Script Executor)
  │           │     │
  │           │     ├─→ Restricted Environment
  │           │     ├─→ Timeout Protection
  │           │     └─→ Return DataFrame
  │           │
  │           └─→ Return Results
  │                 │
  │                 ├─→ Success: Preview + Metadata
  │                 └─→ Failure: Error + Traceback
  │
  └─→ Click "Save Script"
        │
        └─→ POST /api/scripts/create
              │
              └─→ Save to data/scripts.json
```

### 2. Script Usage in Jobs Flow

```
User → Create/Edit Job Page
  │
  ├─→ Click "Load Saved Script"
  │     │
  │     └─→ GET /api/scripts
  │           │
  │           └─→ Display Script List
  │
  ├─→ Select Script
  │     │
  │     └─→ Load script_content into editor
  │
  └─→ Create/Update Job
        │
        └─→ POST /api/jobs/create (or PUT /api/jobs/{name})
              │
              └─→ Save job with processing_script
```

## Data Models

### Script Model
```typescript
{
  script_name: string
  description?: string
  script_content: string
  created_at: datetime
  updated_at: datetime
}
```

### Script Test Request
```typescript
{
  script_content: string
  test_file_path: string
}
```

### Script Test Result
```typescript
{
  success: boolean
  input_shape: [rows, cols]
  output_shape: [rows, cols]
  input_columns: string[]
  output_columns: string[]
  output_preview: object[]
  output_dtypes: Record<string, string>
  error: string | null
  error_type: string | null
  traceback: string | null
}
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                            │
│                                                                  │
│  1. Input Validation                                            │
│     ├─→ Pydantic Models                                         │
│     ├─→ File Type Validation                                    │
│     └─→ Script Content Validation                               │
│                                                                  │
│  2. Execution Sandbox                                           │
│     ├─→ Restricted Built-ins                                    │
│     ├─→ Limited Imports (pandas, numpy, datetime)               │
│     ├─→ No File System Access                                   │
│     └─→ No Network Access                                       │
│                                                                  │
│  3. Resource Limits                                             │
│     ├─→ Execution Timeout                                       │
│     ├─→ Memory Limits (via threading)                           │
│     └─→ File Size Limits                                        │
│                                                                  │
│  4. Error Handling                                              │
│     ├─→ Try-Catch Blocks                                        │
│     ├─→ Graceful Degradation                                    │
│     └─→ Detailed Error Logging                                  │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
ChronoJob/
│
├── app/
│   ├── api/
│   │   ├── jobs.py              # Job management endpoints
│   │   └── scripts.py           # Script management endpoints ✨ NEW
│   │
│   ├── models/
│   │   ├── job.py               # Job data models
│   │   └── script.py            # Script data models ✨ NEW
│   │
│   ├── storage/
│   │   ├── job_storage.py       # Job persistence
│   │   └── script_storage.py    # Script persistence ✨ NEW
│   │
│   ├── executor/
│   │   ├── script_executor.py   # Script execution engine
│   │   └── data_fetcher.py      # Data loading
│   │
│   └── main.py                  # FastAPI app (updated)
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── CreateJob.tsx    # Updated with script selector
│       │   ├── EditJob.tsx      # Updated with script selector
│       │   └── ScriptDebugger.tsx ✨ NEW
│       │
│       ├── types/
│       │   ├── job.ts
│       │   └── script.ts        ✨ NEW
│       │
│       ├── services/
│       │   └── api.ts           # Updated with scriptsApi
│       │
│       └── components/
│           └── Layout.tsx       # Updated with navigation
│
├── data/
│   ├── scripts.json             ✨ NEW
│   ├── jobs.json
│   └── uploads/
│       └── test/                ✨ NEW
│           ├── .gitkeep
│           └── sample_sales.csv ✨ NEW
│
└── docs/
    ├── SCRIPT_DEBUGGER.md                ✨ NEW
    ├── SCRIPT_DEBUGGER_QUICKSTART.md     ✨ NEW
    └── SCRIPT_DEBUGGER_ARCHITECTURE.md   ✨ NEW
```

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Routing**: React Router v6

### Backend
- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **Data Processing**: Pandas + NumPy
- **Async**: asyncio
- **CORS**: FastAPI CORS Middleware

### Storage
- **Format**: JSON files
- **Scripts**: `data/scripts.json`
- **Jobs**: `data/jobs.json`
- **Test Files**: `data/uploads/test/`

## API Endpoints Summary

### Script Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scripts/create` | Create new script |
| PUT | `/api/scripts/{name}` | Update script |
| GET | `/api/scripts` | List all scripts |
| GET | `/api/scripts/{name}` | Get specific script |
| DELETE | `/api/scripts/{name}` | Delete script |
| POST | `/api/scripts/test` | Test script execution |
| POST | `/api/scripts/upload-test-file` | Upload test data |

### Job Management (Existing)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/create` | Create new job |
| PUT | `/api/jobs/{name}` | Update job |
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{name}` | Get specific job |
| DELETE | `/api/jobs/{name}` | Delete job |
| POST | `/api/jobs/{name}/test` | Test job execution |
| POST | `/api/jobs/upload-file` | Upload data file |

## Integration Points

1. **Script Debugger ↔ Script Storage**
   - Save/load scripts
   - CRUD operations

2. **Script Debugger ↔ Script Executor**
   - Test script execution
   - Error handling

3. **Job Creation ↔ Script Storage**
   - Load saved scripts
   - Populate script field

4. **Job Execution ↔ Script Executor**
   - Execute saved scripts
   - Process data

## Performance Considerations

1. **Script Execution**
   - Timeout protection (default: configurable)
   - Threading for isolation
   - Memory limits via process management

2. **File Uploads**
   - Size limits enforced
   - Async file handling
   - Temporary storage cleanup

3. **Data Preview**
   - Limited to first 10 rows
   - Efficient serialization
   - Lazy loading

4. **Script Storage**
   - JSON-based (simple, readable)
   - In-memory caching possible
   - Fast read/write operations
