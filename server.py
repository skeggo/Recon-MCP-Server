#!/usr/bin/env python3
"""
Reconnaissance MCP Server
A modular MCP server using FastMCP for running reconnaissance and footprinting tasks.
"""

import subprocess
import sys
from typing import List
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("recon-server")

@mcp.tool()
def run_tool(tool: str, args: List[str]) -> dict:
    """
    Run a reconnaissance tool with specified arguments.
    
    Args:
        tool (str): The command/tool to run (e.g., 'nmap', 'dig', 'whois')
        args (List[str]): List of arguments to pass to the tool
    
    Returns:
        dict: Contains stdout, stderr, and returncode from the executed command
    """
    try:
        # Combine tool and args into a single command list
        command = [tool] + args
        
        # Run the command with subprocess
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for safety
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(command)
        }
        
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Command timed out after 300 seconds",
            "returncode": -1,
            "command": " ".join([tool] + args)
        }
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": f"Tool '{tool}' not found",
            "returncode": -1,
            "command": " ".join([tool] + args)
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "returncode": -1,
            "command": " ".join([tool] + args)
        }

if __name__ == "__main__":
    # Run the MCP server with stdio transport
    mcp.run(transport="stdio")