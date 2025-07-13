import os
import tempfile
import subprocess
import json
from flask import Flask, request, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

MAX_EXECUTION_TIME = 30
USE_NSJAIL = os.environ.get('USE_NSJAIL', 'false').lower() == 'true'
NSJAIL_CONFIG_PATH = "/app/nsjail-alpine.cfg"

def validate_script(script):
    """Validate that the script contains a main() function."""
    if not script or not script.strip():
        raise ValueError("Script content cannot be empty")
        
    if 'def main(' not in script:
        raise ValueError("Script must contain a 'main()' function")
    
    dangerous_imports = ['os', 'sys', 'subprocess', 'socket', 'urllib', 'requests']
    for dangerous in dangerous_imports:
        if f'import {dangerous}' in script or f'from {dangerous}' in script:
            logger.warning(f"Potentially dangerous import detected: {dangerous}")
    
    return True

def execute_with_subprocess(script_path):
    """Execute Python script using subprocess with timeout."""
    try:
        cmd = ['/usr/local/bin/python3', script_path]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=MAX_EXECUTION_TIME,
            cwd='/tmp'
        )
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        raise ValueError(f'Execution timed out after {MAX_EXECUTION_TIME} seconds')
    except Exception as e:
        raise ValueError(f'Execution error: {str(e)}')

def execute_with_nsjail(script_path):
    """Execute Python script using nsjail for security."""
    try:
        nsjail_script_path = f'/tmp/{os.path.basename(script_path)}'
        
        cmd = [
            'nsjail',
            '--config', NSJAIL_CONFIG_PATH,
            '--',
            '/usr/local/bin/python3', nsjail_script_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=MAX_EXECUTION_TIME + 5,
            cwd='/tmp'
        )
        
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        raise ValueError('Execution timed out')
    except Exception as e:
        raise ValueError(f'nsjail execution error: {str(e)}')

@app.route('/')
def home():
    """API documentation."""
    return jsonify({
        'message': 'Python Code Execution API',
        'version': '2.0-alpine',
        'security': 'nsjail' if USE_NSJAIL else 'subprocess',
        'endpoints': {
            'GET /': 'API documentation',
            'GET /health': 'Health check',
            'POST /execute': 'Execute Python script (requires "script" field with main() function)'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/execute', methods=['POST'])
def execute():
    """Execute Python script."""
    try:
        
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        
        if 'script' not in data:
            return jsonify({'error': "Missing 'script' field in JSON body"}), 400
        
        script = data['script']
        
        if not script or not script.strip():
            return jsonify({'error': 'Script cannot be empty'}), 400
        
        try:
            validate_script(script)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        wrapper_script = f'''
import sys
import json
import io
from contextlib import redirect_stdout

# User's script
{script}

# Execution wrapper
if __name__ == "__main__":
    try:
        # Capture stdout
        stdout_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture):
            result = main()
        
        # Get captured output
        stdout_content = stdout_capture.getvalue()
        
        # Validate that result is JSON serializable
        try:
            json.dumps(result)
        except (TypeError, ValueError) as e:
            raise ValueError(f"main() function must return JSON-serializable data, got: {{type(result).__name__}}")
        
        # Create response
        response = {{
            "result": result,
            "stdout": stdout_content
        }}
        
        print("__RESULT_START__" + json.dumps(response) + "__RESULT_END__")
        
    except Exception as e:
        error_response = {{
            "error": str(e)
        }}
        print("__ERROR_START__" + json.dumps(error_response) + "__ERROR_END__")
        sys.exit(1)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir='/tmp') as f:
            f.write(wrapper_script)
            script_path = f.name
        
        try:
            if USE_NSJAIL and os.path.exists('/usr/local/bin/nsjail'):
                execution_result = execute_with_nsjail(script_path)
            else:
                execution_result = execute_with_subprocess(script_path)
            
            
            output = execution_result['stdout']
            
            
            if "__ERROR_START__" in output and "__ERROR_END__" in output:
                start_marker = "__ERROR_START__"
                end_marker = "__ERROR_END__"
                start_idx = output.find(start_marker) + len(start_marker)
                end_idx = output.find(end_marker)
                error_json = output[start_idx:end_idx]
                
                try:
                    error_data = json.loads(error_json)
                    return jsonify({"error": error_data.get("error", "Script execution failed")}), 400
                except json.JSONDecodeError:
                    return jsonify({"error": "Script execution failed with parsing error"}), 400
            
            if "__RESULT_START__" in output and "__RESULT_END__" in output:
                start_marker = "__RESULT_START__"
                end_marker = "__RESULT_END__"
                start_idx = output.find(start_marker) + len(start_marker)
                end_idx = output.find(end_marker)
                result_json = output[start_idx:end_idx]
                
                try:
                    result_data = json.loads(result_json)
                    return jsonify(result_data)
                except json.JSONDecodeError:
                    return jsonify({"error": "Failed to parse execution result"}), 400
            
            if execution_result['stderr']:
                return jsonify({"error": f"Script execution error: {execution_result['stderr']}"}), 400
            
            return jsonify({"error": "Script execution failed - no result returned"}), 400
            
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
                
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Python Execution API (Alpine)")
    logger.info(f"Security mode: {'nsjail' if USE_NSJAIL else 'subprocess'}")
    logger.info(f"nsjail available: {os.path.exists('/usr/local/bin/nsjail')}")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
