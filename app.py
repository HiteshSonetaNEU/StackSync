import json
import subprocess
import tempfile
import os
import sys
import time
from pathlib import Path
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NSJAIL_CONFIG_PATH = "/app/nsjail.cfg"
PYTHON_TIMEOUT = 30


def validate_script(script_content):
    """
    Validate that the script contains a main() function and basic safety checks
    """
    if not script_content or not script_content.strip():
        raise ValueError("Script content cannot be empty")
    
    if "def main(" not in script_content:
        raise ValueError("Script must contain a 'main()' function")
    
    dangerous_patterns = [
        "import subprocess",
        "import os",
        "__import__",
        "exec(",
        "eval(",
        "open(",
        "file(",
        "input(",
        "raw_input(",
    ]
    
    script_lower = script_content.lower()
    for pattern in dangerous_patterns:
        if pattern in script_lower:
            raise ValueError(f"Script contains potentially dangerous code: {pattern}")
    
    return True


def create_execution_script(user_script):
    """
    Create a wrapper script that captures the main() function result
    """
    wrapper_script = f'''
import sys
import json
import io
from contextlib import redirect_stdout

# User's script
{user_script}

# Execution wrapper
if __name__ == "__main__":
    try:
        # Capture stdout
        stdout_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture):
            result = main()
        
        # Get captured output
        stdout_content = stdout_capture.getvalue()
        
        # Ensure result is JSON serializable
        if result is None:
            result = None
        
        # Create response
        response = {{
            "result": result,
            "stdout": stdout_content,
            "error": None
        }}
        
        print("__RESULT_START__" + json.dumps(response) + "__RESULT_END__")
        
    except Exception as e:
        error_response = {{
            "result": None,
            "stdout": "",
            "error": str(e)
        }}
        print("__RESULT_START__" + json.dumps(error_response) + "__RESULT_END__")
        sys.exit(1)
'''
    return wrapper_script


def execute_with_nsjail(script_content):
    """
    Execute Python script safely using nsjail
    """
    try:
        
        script_dir = '/tmp/scripts'
        os.makedirs(script_dir, exist_ok=True)
    
        script_filename = f"script_{int(time.time() * 1000000)}.py"
        script_path = os.path.join(script_dir, script_filename)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        
        nsjail_script_path = f"/tmp/{script_filename}"
        nsjail_cmd = [
            'nsjail',
            '--config', NSJAIL_CONFIG_PATH,
            '--',
            '/usr/bin/python3', nsjail_script_path  
        ]
        
        
        process = subprocess.run(
            nsjail_cmd,
            capture_output=True,
            text=True,
            timeout=PYTHON_TIMEOUT
        )
        
        
        output = process.stdout
        if "__RESULT_START__" in output and "__RESULT_END__" in output:
            start_marker = "__RESULT_START__"
            end_marker = "__RESULT_END__"
            start_idx = output.find(start_marker) + len(start_marker)
            end_idx = output.find(end_marker)
            result_json = output[start_idx:end_idx]
            
            try:
                return json.loads(result_json)
            except json.JSONDecodeError:
                pass
        
        
        return {
            "result": None,
            "stdout": process.stdout,
            "error": process.stderr if process.stderr else "Failed to parse execution result"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "result": None,
            "stdout": "",
            "error": f"Script execution timed out after {PYTHON_TIMEOUT} seconds"
        }
    except Exception as e:
        return {
            "result": None,
            "stdout": "",
            "error": f"Execution error: {str(e)}"
        }
    finally:
        try:
            if 'script_path' in locals() and os.path.exists(script_path):
                os.unlink(script_path)
        except Exception:
            pass


@app.route('/execute', methods=['POST'])
def execute_script():
    """
    Execute Python script endpoint
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' field in JSON body"}), 400
        
        script_content = data['script']
        
        try:
            validate_script(script_content)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        execution_script = create_execution_script(script_content)
        
        result = execute_with_nsjail(execution_script)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            "result": None,
            "stdout": "",
            "error": "Internal server error"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy"})


@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint with API documentation
    """
    return jsonify({
        "message": "Secure Python Code Execution API",
        "endpoints": {
            "POST /execute": "Execute Python script with main() function",
            "GET /health": "Health check",
            "GET /": "API documentation"
        },
        "example_request": {
            "script": "def main():\\n    return {'message': 'Hello World', 'result': 42}"
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
