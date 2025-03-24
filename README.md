# GooseForceOAuth

A Salesforce OAuth extension for Goose that allows secure authentication with Salesforce orgs.

## Features
- Secure OAuth 2.0 implementation
- Support for sandbox and production orgs
- Secure credential storage using system keychain
- Per-org Connected App support

## Setup Instructions

### For Administrators
1. Create a Connected App in your Salesforce org:
   - Go to Setup > App Manager
   - Click "New Connected App"
   - Fill in:
     - Connected App Name: Goose for Salesforce
     - API Name: Goose_for_Salesforce
     - Contact Email: [your admin email]
   - Enable OAuth Settings:
     - Check "Enable OAuth Settings"
     - Callback URL: http://localhost:8787
     - Selected OAuth Scopes:
       - Access and manage your data (api)
       - Perform requests on your behalf at any time (refresh_token)
       - Full access (full)
     - Check "Require Secret for Web Server Flow" only
   - Click Save
2. After saving, wait ~10 minutes for settings to propagate
3. Get the Consumer Key from Manage > View Consumer Details
4. Share the Consumer Key with your team

### For Users
1. Install the Goose extension
2. First time setup:
   - Enter the Consumer Key provided by your admin
   - Select sandbox or production environment
   - Authorize the application
3. Subsequent uses will use the stored configuration

## Requirements
- Python 3.8+
- Goose Desktop Application
- Access to a Salesforce org

## Installation
```bash
# Clone the repository
git clone https://github.com/tnohrer/GooseForceOAuth.git

# Install dependencies
pip install -r requirements.txt
```

## Security
- No hardcoded credentials
- Secure storage using system keychain
- Per-org Connected Apps
- Standard OAuth 2.0 security practices


## Technical Break Down
1. login_handler.py - Core Authentication File
```bash
class LoginHandler:
    # Handles the main OAuth flow
    # Stores/retrieves Consumer Key from keychain
    # Manages Salesforce connection
```
Use:
- Manages the OAuth authentication process
- Handles secure storage of Consumer Key
- Creates and maintains Salesforce connection
- Processes OAuth callbacks

2. auth_state.py - State Management
```bash
class AuthState(Enum):
    INITIAL = "initial"
    WAITING_FOR_CONFIG = "waiting_for_config"
    OAUTH_FLOW = "oauth_flow"
    COMPLETED = "completed"
```
Use:
- Tracks where user is in authentication process
- Helps manage flow transitions
- Makes error handling clearer
- Improves user experience

3. config_handler.py - Configuration UI
```bash
class ConfigurationHandler(BaseHTTPRequestHandler):
    # Shows configuration page
    # Collects Consumer Key from user
    # Validates input
```
Use:
- Provides UI for first-time setup
- Collects Consumer Key securely
- Shows admin setup instructions
- Handles configuration storage

4. environment_selector.py - Environment Selection
```bash
class EnvironmentSelector:
    # Shows sandbox/production selector
    # Handles environment choice
```
Use:
- Lets users choose between sandbox/production
- Manages environment-specific URLs
- Handles environment selection UI

5. server.py - Main Extension Server
```bash
class TheGooseForceExtension(FastMCP):
    # Main extension implementation
    # Sets up available tools
    # Manages extension lifecycle
```
Use:
- Integrates with Goose platform
- Provides tool interfaces (login, query, etc.)
- Manages extension lifecycle
- Handles error reporting

6. templates/ - HTML Templates
```bash
templates/
├── environment_selector.html   # Environment selection page
└── oauth_callback.html        # OAuth callback page
```
Use:
- Provides user interfaces
- Handles OAuth callbacks
- Shows configuration screens

7. init.py - Module Initialization
```bash
# Makes the directory a Python package
# Exports necessary classes
```
Use:
- Makes the code a proper Python package
- Controls what's available to import
- Sets up module structure

8. main.py - Entry Point
```bash
# Starts the extension server
# Sets up logging
```
Use:
- Provides entry point for running extension
- Sets up initial configuration
- Starts necessary services

# The Flow between the Files:
```bash
1. User starts extension
   ↓
2. server.py initializes
   ↓
3. environment_selector.py shows environment choice
   ↓
4. login_handler.py starts OAuth flow
   ↓
5. config_handler.py shows setup if needed
   ↓
6. auth_state.py tracks progress
   ↓
7. Templates provide UI
   ↓
8. Connected to Salesforce!
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
