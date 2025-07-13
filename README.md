# Python Code Execution API

A secure, containerized Python code execution service deployed on Google Cloud Run with Alpine Linux optimization.

## 🚀 Features

- **Secure Execution**: Subprocess-based Python code execution with timeout controls
- **RESTful API**: Simple JSON-based API for code execution
- **Alpine Optimized**: 86% smaller Docker image (325MB vs 2.31GB)
- **Cloud Ready**: Deployed on Google Cloud Run with auto-scaling
- **Health Monitoring**: Built-in health check endpoints

## 📊 Optimization Results

| Metric | Original | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Image Size | 2.31GB | 325MB | 86% reduction |
| Base OS | Ubuntu 22.04 | Alpine Linux 3.18 | Minimal footprint |
| Deployment Speed | Slow | Fast | Faster cold starts |

## 🌐 Deployed Service

**Service URL**: `https://python-executor-317362064963.us-central1.run.app`

## 🧪 Testing with Google Cloud SDK

### Prerequisites
- Google Cloud SDK installed and authenticated
- PowerShell (Windows) or equivalent terminal

### Simple 2+2 Example

Test the deployed service with a simple addition function:

```powershell
# Create the request body
$body = @{
    script = @"
def main():
    result = 2 + 2
    print(f'Calculating: 2 + 2')
    return result
"@
} | ConvertTo-Json

# Send the request to Google Cloud Run
Invoke-RestMethod -Uri "https://python-executor-317362064963.us-central1.run.app/execute" -Method POST -Body $body -ContentType "application/json"
```

**Expected Output:**
```json
{
  "result": 4,
  "stdout": "Calculating: 2 + 2\n"
}
```

### Health Check Example

```powershell
# Test the health endpoint
Invoke-RestMethod -Uri "https://python-executor-317362064963.us-central1.run.app/health" -Method GET
```

**Expected Output:**
```json
{
  "status": "healthy"
}
```

### Advanced Example

Test with more complex operations:

```powershell
$body = @{
    script = @"
import math

def main():
    print('Starting mathematical operations...')
    
    # Multiple operations
    results = {
        'addition': 2 + 2,
        'multiplication': 5 * 6,
        'square_root': math.sqrt(16),
        'factorial': math.factorial(5),
        'powers': [2**i for i in range(5)]
    }
    
    print('Operations completed:')
    for operation, value in results.items():
        print(f'  {operation}: {value}')
    
    return results
"@
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://python-executor-317362064963.us-central1.run.app/execute" -Method POST -Body $body -ContentType "application/json"
```

**Expected Output:**
```json
{
  "result": {
    "addition": 4,
    "multiplication": 30,
    "square_root": 4.0,
    "factorial": 120,
    "powers": [1, 2, 4, 8, 16]
  },
  "stdout": "Starting mathematical operations...\nOperations completed:\n  addition: 4\n  multiplication: 30\n  square_root: 4.0\n  factorial: 120\n  powers: [1, 2, 4, 8, 16]\n"
}
```

## 🌟 Quick Production API Examples

### Simple Calculator Example

```powershell
# Test basic arithmetic
$body = @{
    script = @"
def main():
    x = 10
    y = 5
    result = x * y
    print(f'{x} * {y} = {result}')
    return result
"@
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://python-executor-317362064963.us-central1.run.app/execute" -Method POST -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "result": 50,
  "stdout": "10 * 5 = 50\n"
}
```

### Data Analysis Example

```powershell
# Process a list of numbers
$body = @{
    script = @"
def main():
    numbers = [10, 20, 30, 40, 50]
    total = sum(numbers)
    average = total / len(numbers)
    
    print(f'Numbers: {numbers}')
    print(f'Total: {total}')
    print(f'Average: {average}')
    
    return {
        'numbers': numbers,
        'total': total,
        'average': average,
        'max': max(numbers),
        'min': min(numbers)
    }
"@
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://python-executor-317362064963.us-central1.run.app/execute" -Method POST -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "result": {
    "numbers": [10, 20, 30, 40, 50],
    "total": 150,
    "average": 30.0,
    "max": 50,
    "min": 10
  },
  "stdout": "Numbers: [10, 20, 30, 40, 50]\nTotal: 150\nAverage: 30.0\n"
}
```

### One-Liner Test

```powershell
# Quick test
$body = '{"script":"def main():\n    return 2+2"}' 
Invoke-RestMethod -Uri "https://python-executor-317362064963.us-central1.run.app/execute" -Method POST -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "result": 4,
  "stdout": ""
}
```

## 📋 API Endpoints

### POST /execute
Execute Python code with a required `main()` function that returns JSON-serializable data.

**Request Body:**
```json
{
  "script": "def main():\n    print('Hello World')\n    return {'message': 'success', 'value': 42}"
}
```

**Success Response:**
```json
{
  "result": {
    "message": "success", 
    "value": 42
  },
  "stdout": "Hello World\n"
}
```

**Error Response:**
```json
{
  "error": "Script must contain a 'main()' function"
}
```

**Requirements:**
- Script must contain a `main()` function
- `main()` function must return JSON-serializable data
- Dangerous imports (`subprocess`, `os`, etc.) are blocked

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /
API documentation and example usage.

## 🔧 Local Development

### Build and Run Locally

```bash
# Build the optimized Alpine image
docker build -t python-executor .

# Run locally on port 8080
docker run -d -p 8080:8080 --name python-executor-local python-executor

# Check if container is running
docker ps
```

### Local Testing Examples

#### Simple Addition Test
```powershell
# Test basic functionality
$body = @{
    script = @"
def main():
    result = 2 + 2
    print(result)
    return result
"@
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8080/execute" -Method POST -Body $body -ContentType "application/json"
Write-Host "Result:" $response.result
Write-Host "Stdout:" $response.stdout
```

**Expected Output:**
```
Result: 4
Stdout: 4
```

#### Complex Data Processing Test
```powershell
# Test with complex JSON return
$body = @{
    script = @"
def main():
    print('Processing employee data...')
    
    employees = ['Alice', 'Bob', 'Charlie']
    salaries = [75000, 65000, 80000]
    
    total_salary = sum(salaries)
    avg_salary = total_salary / len(salaries)
    
    print(f'Total employees: {len(employees)}')
    print(f'Average salary: ${avg_salary:,.2f}')
    
    return {
        'employees': employees,
        'total_salary': total_salary,
        'average_salary': round(avg_salary, 2),
        'employee_count': len(employees)
    }
"@
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/execute" -Method POST -Body $body -ContentType "application/json"
```

#### Health Check Test
```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET
```

#### Error Handling Test
```powershell
# Test script without main() function (should fail)
$body = @{
    script = "def hello(): return 'world'"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8080/execute" -Method POST -Body $body -ContentType "application/json"
} catch {
    Write-Host "Error (Expected):" $_.ErrorDetails.Message
}
```

### Cleanup Local Container
```bash
# Stop and remove local container
docker stop python-executor-local
docker rm python-executor-local
```

## 🚀 Deployment to Google Cloud Run

### Prerequisites
- Google Cloud SDK installed
- Docker installed
- Project configured: `stacksync-465620`

### Deploy Steps

```bash
# 1. Build and tag the image
docker build -t python-executor .
docker tag python-executor gcr.io/stacksync-465620/python-executor:alpine

# 2. Push to Google Container Registry
docker push gcr.io/stacksync-465620/python-executor:alpine

# 3. Deploy to Cloud Run
gcloud run deploy python-executor \
  --image gcr.io/stacksync-465620/python-executor:alpine \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1
```

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── app-minimal.py         # Minimal version with subprocess execution
├── requirements.txt       # Python dependencies
├── Dockerfile            # Optimized Alpine Dockerfile
├── nsjail-alpine.cfg     # nsjail configuration for Alpine
├── nsjail-cloudrun.cfg   # nsjail configuration for Cloud Run
├── nsjail.cfg           # Base nsjail configuration
└── README.md            # This file
```

## 🔒 Security Features

- **Input Validation**: Requires `main()` function, blocks dangerous imports
- **Subprocess Isolation**: Code runs in isolated subprocess with timeout
- **Resource Limits**: Memory and CPU constraints via Cloud Run
- **Network Security**: Controlled access through Cloud Run's security model

## 🐛 Troubleshooting

### Common Issues

1. **Script Validation Error**: Ensure your script contains a `main()` function
   ```json
   {"error": "Script must contain a 'main()' function"}
   ```

2. **JSON Serialization Error**: The `main()` function must return JSON-serializable data
   ```json
   {"error": "main() function must return JSON-serializable data, got: object"}
   ```

3. **Timeout Error**: Scripts must complete within 30 seconds
   ```json
   {"error": "Script execution timed out after 30 seconds"}
   ```

4. **Import Restrictions**: Some imports are blocked for security
   ```json
   {"error": "Script contains potentially dangerous code: import os"}
   ```

### Example Valid Script
```python
def main():
    # This works - returns JSON-serializable data
    print("Processing data...")
    return {
        "status": "success",
        "result": 42,
        "data": [1, 2, 3, 4, 5]
    }
```

### Example Invalid Scripts
```python
# ❌ Missing main() function
def hello():
    return "world"

# ❌ Returns non-JSON serializable object  
def main():
    return object()

# ❌ Contains dangerous import
import os
def main():
    return "hello"
```

## 📝 Requirements

- Python 3.11
- Flask
- Alpine Linux 3.18 (in container)
- Google Cloud Run (for deployment)

## 🏗️ Architecture

- **Base Image**: `python:3.11-alpine3.18`
- **Execution Method**: Subprocess with timeout controls
- **Security**: Input validation and restricted imports
- **Optimization**: Multi-stage Docker builds for minimal image size

## 📊 Performance

- **Cold Start**: ~2-3 seconds (optimized with Alpine)
- **Execution Timeout**: 30 seconds maximum
- **Memory Usage**: 1GB allocated, typically uses <100MB
- **Concurrent Requests**: Auto-scales based on demand

## 📄 License

This project is licensed under the MIT License.
