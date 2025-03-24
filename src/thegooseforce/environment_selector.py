"""Environment selector for TheGooseForce."""
import logging
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import socket
import json
import urllib.parse
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TheGooseForce - Salesforce Login</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            width: 400px;
        }
        h1 {
            color: #1a73e8;
            margin-bottom: 1.5rem;
        }
        .button-group {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin: 2rem 0;
        }
        .button {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
            width: 100%;
        }
        .production {
            background-color: #1a73e8;
            color: white;
        }
        .production:hover {
            background-color: #1557b0;
        }
        .sandbox {
            background-color: #34a853;
            color: white;
        }
        .sandbox:hover {
            background-color: #2d8745;
        }
        .cancel {
            background-color: #f5f5f5;
            color: #666;
            border: 1px solid #ddd;
        }
        .cancel:hover {
            background-color: #e8e8e8;
        }
        #status {
            margin-top: 1rem;
            color: #666;
        }
        .error {
            color: #d93025;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Select Salesforce Environment</h1>
        <div class="button-group">
            <button class="button production" onclick="selectEnvironment('production')">
                Salesforce Production
            </button>
            <button class="button sandbox" onclick="selectEnvironment('sandbox')">
                Salesforce Sandbox
            </button>
            <button class="button cancel" onclick="selectEnvironment('cancel')">
                Cancel
            </button>
        </div>
        <div id="status"></div>
    </div>
    <script>
        function setStatus(message, isError = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = isError ? 'error' : '';
        }
        
        async function selectEnvironment(env) {
            try {
                setStatus('Processing selection...');
                const response = await fetch('/select?env=' + encodeURIComponent(env));
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.status === 'ok') {
                        setStatus('Selection successful! Redirecting...');
                        window.close();
                    } else {
                        setStatus(data.message || 'Error processing selection', true);
                    }
                } else {
                    setStatus('Error processing selection. Please try again.', true);
                }
            } catch (error) {
                console.error('Error:', error);
                setStatus('Error: ' + error.message, true);
            }
        }
    </script>
</body>
</html>
"""

class SelectorHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                # Serve selector page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                self.wfile.write(HTML_TEMPLATE.encode())
                
            elif self.path.startswith('/select'):
                # Handle environment selection
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                
                if 'env' in params:
                    environment = params['env'][0]
                    self.server.selected_environment = environment
                    self.server.selection_event.set()
                    
                    # Return success
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "error",
                        "message": "No environment specified"
                    }).encode())
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": str(e)
            }).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.debug(f"Selector: {format%args}")

class EnvironmentSelector:
    def __init__(self):
        self.server = None
        self.thread = None
        
    def _find_available_port(self, start_port: int = 8787, max_attempts: int = 10) -> int:
        """Find an available port starting from start_port."""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("Could not find an available port")
    
    def show(self) -> Optional[Dict[str, Any]]:
        """Show the environment selector and return the selected environment."""
        try:
            # Find available port
            port = self._find_available_port()
            
            # Create server with selection event
            self.server = HTTPServer(('127.0.0.1', port), SelectorHandler)
            self.server.selected_environment = None
            self.server.selection_event = threading.Event()
            
            # Start server in thread
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            
            # Open browser
            url = f"http://127.0.0.1:{port}"
            logger.info(f"Opening environment selector: {url}")
            webbrowser.open(url)
            
            # Wait for selection
            logger.info("Waiting for environment selection...")
            if self.server.selection_event.wait(timeout=60):  # Wait up to 60 seconds
                if self.server.selected_environment == 'cancel':
                    logger.info("Selection cancelled by user")
                    return None
                    
                if self.server.selected_environment:
                    logger.info(f"Environment selected: {self.server.selected_environment}")
                    return {"environment": self.server.selected_environment}
            
            logger.info("No environment selected or timeout")
            return None
            
        except Exception as e:
            logger.error(f"Environment selection failed: {e}")
            return None
        finally:
            # Cleanup
            if self.server:
                logger.info("Shutting down environment selector server...")
                self.server.shutdown()
                self.server.server_close()
                logger.info("Server shutdown complete")