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

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
