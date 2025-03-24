"""State management for Salesforce authentication flow."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class AuthState(Enum):
    INITIAL = "initial"
    SANDBOX_LOGIN = "sandbox_login"
    WAITING_FOR_CONFIG = "waiting_for_config"
    OAUTH_FLOW = "oauth_flow"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AuthContext:
    """Holds the current state and data for the authentication flow."""
    state: AuthState = AuthState.INITIAL
    environment: str = "sandbox"
    instance_url: Optional[str] = None
    error_message: Optional[str] = None
    
    def update_state(self, new_state: AuthState, error: Optional[str] = None):
        """Update the current state and optionally set an error message."""
        self.state = new_state
        self.error_message = error