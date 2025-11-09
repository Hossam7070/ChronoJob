#!/bin/bash
export ENVIRONMENT=test
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_USER=test@example.com
export SMTP_PASSWORD=test_password
export SMTP_FROM_EMAIL=chronojob@example.com

echo "Starting ChronoJob Backend in TEST mode..."
echo "Email sending is DISABLED"
echo ""

source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
