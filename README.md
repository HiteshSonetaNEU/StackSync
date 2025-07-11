# Secure Python Code Execution API

A Flask-based API service that safely executes arbitrary Python code using nsjail for sandboxing.

## Features

- **Secure Execution**: Uses nsjail to sandbox Python script execution
- **REST API**: Simple `/execute` endpoint accepting Python scripts
- **Input Validation**: Validates scripts for required `main()` function and security
- **Resource Limits**: Configurable CPU, memory, and time limits
- **Docker Support**: Lightweight container for easy deployment
- **Cloud Run Ready**: Designed for Google Cloud Run deployment

## Quick Start

### Local Development

1. **Prerequisites**:
   - Docker installed
   - Python 3.11+ (for local testing)

2. **Clone and Build**:
   ```bash
   git clone <your-repository-url>
   cd python-execution-api
   ```

3. **Build Docker Image**:
   ```bash
   docker build -t python-executor .
   ```

4. **Run Locally**:
   ```bash
   docker run -p 8080:8080 python-executor
   ```

### API Usage

#### Execute Python Script

**Endpoint**: `POST /execute`

**Request Body**:
```json
{
  "script": "def main():\n    return {'message': 'Hello World', 'numbers': [1, 2, 3]}"
}
```

**Response**:
```json
{
  "result": {
    "message": "Hello World", 
    "numbers": [1, 2, 3]
  },
  "stdout": "",
  "error": null
}
```

#### Example cURL Requests

**Local Testing**:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import json\n    return {\"result\": 42, \"message\": \"success\"}"
  }'
```

**Cloud Run** (replace with your actual URL):
```bash
curl -X POST https://python-executor-xxxxxxxxx-uc.a.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    import pandas as pd\n    import numpy as np\n    data = pd.DataFrame({\"x\": [1,2,3], \"y\": [4,5,6]})\n    return {\"mean_x\": float(np.mean(data[\"x\"])), \"shape\": list(data.shape)}"
  }'
```

**With Print Statements**:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    print(\"Processing data...\")\n    result = sum([1, 2, 3, 4, 5])\n    print(f\"Sum calculated: {result}\")\n    return {\"total\": result}"
  }'
```

### Supported Libraries

The sandboxed environment includes:
- **Standard Library**: json, math, datetime, etc.
- **NumPy**: For numerical computations
- **Pandas**: For data manipulation
- **Basic I/O**: Limited file operations in `/tmp`

### Security Features

1. **Process Isolation**: nsjail creates isolated namespaces
2. **Resource Limits**: 
   - CPU: 10 seconds max
   - Memory: 512MB max
   - File size: 10MB max
   - Processes: 5 max
3. **Network Isolation**: No network access from scripts
4. **Input Validation**: Blocks dangerous function calls
5. **Timeout Protection**: 30-second execution limit

### Deployment

#### Google Cloud Run

1. **Build and Push to Container Registry**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/python-executor
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy python-executor \
     --image gcr.io/YOUR_PROJECT_ID/python-executor \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 1Gi \
     --cpu 1 \
     --timeout 60 \
     --max-instances 10
   ```

3. **Get Service URL**:
   ```bash
   gcloud run services describe python-executor --region us-central1 --format 'value(status.url)'
   ```

## API Endpoints

### `POST /execute`
Execute a Python script containing a `main()` function.

**Request**: JSON with `script` field
**Response**: JSON with `result`, `stdout`, and `error` fields

### `GET /health`
Health check endpoint.

**Response**: `{"status": "healthy"}`

### `GET /`
API documentation and examples.

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Successful execution
- `400`: Invalid input (missing main function, dangerous code, etc.)
- `500`: Internal server error

## Development

### Local Testing Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Note: nsjail is required for full functionality
# On Ubuntu/Debian:
sudo apt-get install nsjail

# Run the app
python app.py
```

### Configuration

Edit `nsjail.cfg` to modify sandbox settings:
- Resource limits
- Available libraries
- File system access
- Network policies

## Limitations

- Scripts must contain a `main()` function
- No network access from executed scripts
- Limited file system access (only `/tmp`)
- Some Python modules may be restricted for security

## Troubleshooting

1. **Container won't start**: Check Docker logs
   ```bash
   docker logs <container-id>
   ```

2. **Script execution fails**: Check if script has `main()` function

3. **Import errors**: Verify library is available in the sandbox environment

## License

This project is provided as-is for educational and evaluation purposes.
