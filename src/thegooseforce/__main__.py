"""Main entry point for thegooseforce"""
import asyncio
from thegooseforce.server import run_mcp_server

def main():
    """TheGooseForce: Salesforce integration for Goose."""
    asyncio.run(run_mcp_server())

if __name__ == "__main__":
    main()