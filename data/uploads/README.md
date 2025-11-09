# Data Uploads Directory

This directory stores uploaded data files for jobs that use internal file sources.

## File Path Convention

When creating or editing a job with an internal file source, files should be placed in this directory and referenced using the path format:

```
/data/uploads/filename.csv
```

or

```
/data/uploads/filename.json
```

## Supported File Types

- **CSV**: Comma-separated values files
- **JSON**: JSON format files (should contain an array of objects or a single object)

## Notes

- File paths starting with `/` are resolved relative to the project root
- The system automatically resolves paths to absolute paths during execution
- Ensure uploaded files have the correct format and structure for your processing scripts
