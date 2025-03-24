"""Configuration screen handler for TheGooseForce."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class ConfigurationHandler(BaseHTTPRequestHandler):
    """Handler for configuration screen."""
    
    def do_GET(self):
        """Serve the configuration page."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Goose for Salesforce Configuration</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    h1 {
                        color: #1a73e8;
                        margin-bottom: 20px;
                    }
                    .instructions {
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 4px;
                        margin: 20px 0;
                    }
                    .instructions ol {
                        margin: 0;
                        padding-left: 20px;
                    }
                    input[type="text"] {
                        width: 100%;
                        padding: 8px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 16px;
                    }
                    button {
                        background: #1a73e8;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                    }
                    button:hover {
                        background: #1557b0;
                    }
                    .error {
                        color: #d93025;
                        margin-top: 10px;
                    }
                    .important {
                        background: #e8f0fe;
                        padding: 10px;
                        border-left: 4px solid #1a73e8;
                        margin: 10px 0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Goose for Salesforce Configuration</h1>
                    
                    <div class="instructions">
                        <h3>First Time Setup</h3>
                        <p>To use Goose with Salesforce, you need to enter your org's Consumer Key. 
                           If you don't have this, please ask your Salesforce Administrator to:</p>
                        <ol>
                            <li>Go to Setup > App Manager</li>
                            <li>Click "New Connected App"</li>
                            <li>Fill in:
                                <ul>
                                    <li>Connected App Name: Goose for Salesforce</li>
                                    <li>API Name: Goose_for_Salesforce</li>
                                    <li>Contact Email: [admin email]</li>
                                </ul>
                            </li>
                            <li>Under "API (Enable OAuth Settings)":
                                <ul>
                                    <li>Check "Enable OAuth Settings" to show OAuth options</li>
                                    <li>Set Callback URL: http://localhost:8787</li>
                                    <li>Select OAuth Scopes:
                                        <ul>
                                            <li>Access and manage your data (api)</li>
                                            <li>Perform requests on your behalf at any time (refresh_token)</li>
                                            <li>Full access (full)</li>
                                        </ul>
                                    </li>
                                    <li class="important">Important: Check "Require Secret for Web Server Flow" only</li>
                                </ul>
                            </li>
                            <li>Click Save</li>
                            <li>After saving, wait ~10 minutes for settings to propagate</li>
                            <li>Click "Manage" then "View Consumer Details" to get the Consumer Key</li>
                        </ol>
                    </div>

                    <form id="configForm">
                        <label for="consumer_key">Consumer Key:</label><br>
                        <input type="text" id="consumer_key" name="consumer_key" 
                               placeholder="Enter your org's Consumer Key" required><br>
                        <button type="submit">Save Configuration</button>
                    </form>
                    <div id="error" class="error"></div>
                </div>

                <script>
                    document.getElementById('configForm').onsubmit = function(e) {
                        e.preventDefault();
                        var consumerKey = document.getElementById('consumer_key').value;
                        
                        // Basic validation
                        if (!consumerKey || consumerKey.length < 10) {
                            document.getElementById('error').textContent = 
                                'Please enter a valid Consumer Key';
                            return;
                        }
                        
                        // Submit configuration
                        fetch('/submit?consumer_key=' + encodeURIComponent(consumerKey))
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    document.body.innerHTML = '<div class="container">' +
                                        '<h1>Configuration Successful!</h1>' +
                                        '<p>You can now close this window and continue using ' +
                                        'Goose for Salesforce.</p></div>';
                                } else {
                                    document.getElementById('error').textContent = 
                                        data.error || 'Configuration failed';
                                }
                            })
                            .catch(error => {
                                document.getElementById('error').textContent = 
                                    'Error saving configuration';
                            });
                    };
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/submit'):
            # Handle configuration submission
            query = parse_qs(urlparse(self.path).query)
            consumer_key = query.get('consumer_key', [None])[0]
            
            if consumer_key:
                try:
                    # Store the consumer key
                    self.server.consumer_key = consumer_key
                    self.server.config_received.set()
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": "Configuration saved"
                    }).encode())
                except Exception as e:
                    logger.error(f"Error saving configuration: {str(e)}")
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "error": f"Error saving configuration: {str(e)}"
                    }).encode())
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Invalid Consumer Key"
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.debug(f"Configuration Server: {format%args}")