"""TheGooseForce Extension for Goose."""
import logging
from typing import Dict, Any, Optional
import webbrowser
from mcp.server.fastmcp.server import FastMCP
from simple_salesforce import Salesforce
from .login_handler import LoginHandler

logger = logging.getLogger(__name__)

class TheGooseForceExtension(FastMCP):
    """TheGooseForce Extension."""

    def __init__(self):
        """Initialize the extension."""
        super().__init__(
            name="thegooseforce",
            display_name="TheGooseForce",
            description="Salesforce integration for Goose",
        )
        self.login_handler = LoginHandler()
        self._setup_tools()
        
    def _setup_tools(self):
        """Set up the extension's tools."""
        @self.tool("thegooseforce_login")
        async def login(
            environment: str = None
        ) -> dict:
            """Login to Salesforce."""
            try:
                # Show environment selector if not provided
                if not environment:
                    from .environment_selector import EnvironmentSelector
                    selector = EnvironmentSelector()
                    result = selector.show()
                    
                    if not result or result.get("environment") == "cancel":
                        return {
                            "success": False,
                            "error": "Login cancelled"
                        }
                    
                    environment = result["environment"]
                
                # Start login flow with selected environment
                return self.login_handler.start_login_flow(environment)
                
            except Exception as e:
                logger.error(f"Login failed: {str(e)}")
                return {"success": False, "error": str(e)}

        @self.tool("thegooseforce_handle_oauth")
        async def handle_oauth(
            callback_url: str
        ) -> dict:
            """Handle OAuth callback."""
            try:
                return self.login_handler.handle_oauth_callback(callback_url)
            except Exception as e:
                logger.error(f"OAuth callback failed: {str(e)}")
                return {"success": False, "error": str(e)}

        @self.tool("thegooseforce_logout")
        async def logout() -> dict:
            """Logout from Salesforce."""
            try:
                self.login_handler.clear_session()
                return {"success": True, "message": "Successfully logged out"}
            except Exception as e:
                logger.error(f"Logout failed: {str(e)}")
                return {"success": False, "error": str(e)}

        @self.tool("thegooseforce_query")
        async def query(soql: str) -> dict:
            """Execute a SOQL query."""
            try:
                sf = self.login_handler.get_sf()
                if not sf:
                    return {
                        "success": False,
                        "error": "Not authenticated. Please login first using thegooseforce_login"
                    }
                
                # Execute query
                try:
                    logger.info(f"Executing SOQL query: {soql}")
                    results = sf.query_all(soql)
                    return {"success": True, "results": results}
                except Exception as e:
                    # If query fails due to session expiry, clear session
                    if "INVALID_SESSION_ID" in str(e):
                        logger.warning("Session expired, clearing session")
                        self.login_handler.clear_session()
                        return {
                            "success": False,
                            "error": "Session expired. Please login again."
                        }
                    raise
                    
            except Exception as e:
                logger.error(f"Query failed: {str(e)}")
                return {"success": False, "error": str(e)}

def run_mcp_server():
    """Run the extension server."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extension = TheGooseForceExtension()
    extension.run()

if __name__ == "__main__":
    run_mcp_server()