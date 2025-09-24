#!/usr/bin/env python3
"""
Reconnaissance MCP Server
A modular MCP server using FastMCP for running reconnaissance and footprinting tasks.
"""

import subprocess
import sys
from typing import List, Optional
from ftplib import FTP
import socket
import os
import paramiko
import tempfile
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("recon-server")

@mcp.tool()
def check_ftp_login(ip: str, username: str = "anonymous", password: str = "anonymous@example.com", port: int = 21, timeout: int = 10) -> dict:
    """
    Check FTP login with custom or anonymous credentials and list files/directories if successful.
    
    Args:
        ip (str): Target IP address to check
        username (str): FTP username (default: "anonymous")
        password (str): FTP password (default: "anonymous@example.com")
        port (int): FTP port (default: 21)
        timeout (int): Connection timeout in seconds (default: 10)
    
    Returns:
        dict: Contains success status, message, and directory listing if successful
    """
    try:
        # Create FTP connection
        ftp = FTP()
        ftp.set_debuglevel(0)
        
        # Set timeout and connect
        ftp.connect(ip, port, timeout)
        
        # Attempt login with provided credentials
        response = ftp.login(username, password)
        
        # Get welcome message
        welcome = ftp.getwelcome()
        
        # Get current working directory
        try:
            current_dir = ftp.pwd()
        except:
            current_dir = "/"
        
        # List files and directories
        files_and_dirs = []
        detailed_listing = []
        
        try:
            # Get simple file list
            file_list = ftp.nlst()
            
            # Get detailed directory listing
            detailed_lines = []
            ftp.retrlines('LIST', detailed_lines.append)
            
            # Parse detailed listing
            for line in detailed_lines:
                parts = line.split()
                if len(parts) >= 9:
                    permissions = parts[0]
                    size = parts[4] if len(parts) > 4 else "unknown"
                    name = " ".join(parts[8:])
                    
                    item_type = "directory" if permissions.startswith('d') else "file"
                    
                    detailed_listing.append({
                        "name": name,
                        "type": item_type,
                        "permissions": permissions,
                        "size": size,
                        "raw_line": line
                    })
            
            # Simple list for backward compatibility
            files_and_dirs = file_list if file_list else [item["name"] for item in detailed_listing]
            
        except Exception as list_error:
            files_and_dirs = []
            detailed_listing = []
            list_error_msg = str(list_error)
        else:
            list_error_msg = None
        
        # Close connection
        ftp.quit()
        
        # Determine login type
        login_type = "anonymous" if username.lower() == "anonymous" else "custom_credentials"
        
        success_message = f"SUCCESS: FTP {login_type} login successful"
        if detailed_listing:
            success_message += f" - Found {len(detailed_listing)} items"
        
        return {
            "success": True,
            "message": success_message,
            "ip": ip,
            "port": port,
            "username": username,
            "login_type": login_type,
            "welcome_message": welcome,
            "login_response": response,
            "current_directory": current_dir,
            "files_and_directories": files_and_dirs,
            "detailed_listing": detailed_listing,
            "total_items": len(detailed_listing),
            "directories": [item for item in detailed_listing if item["type"] == "directory"],
            "files": [item for item in detailed_listing if item["type"] == "file"],
            "list_error": list_error_msg
        }
        
    except socket.timeout:
        return {
            "success": False,
            "message": f"Connection timeout to {ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "error": "timeout"
        }
    except socket.gaierror as e:
        return {
            "success": False,
            "message": f"DNS resolution failed for {ip}",
            "ip": ip,
            "port": port,
            "username": username,
            "error": str(e)
        }
    except ConnectionRefusedError:
        return {
            "success": False,
            "message": f"Connection refused to {ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "error": "connection_refused"
        }
    except Exception as e:
        error_msg = str(e).lower()
        if "530" in error_msg or "login" in error_msg or "authentication" in error_msg:
            return {
                "success": False,
                "message": f"FTP login denied for {username} on {ip}:{port}",
                "ip": ip,
                "port": port,
                "username": username,
                "error": "login_denied"
            }
        else:
            return {
                "success": False,
                "message": f"Error checking FTP login: {str(e)}",
                "ip": ip,
                "port": port,
                "username": username,
                "error": str(e)
            }


@mcp.tool()
def check_ftp_anonymous(ip: str, port: int = 21, timeout: int = 10) -> dict:
    """
    Check if FTP anonymous login is allowed on a target IP.
    This function now calls the enhanced check_ftp_login function.
    """
    return check_ftp_login(ip, "anonymous", "anonymous@example.com", port, timeout)

@mcp.tool()
def ftp_download_file(ip: str, remote_file: str, local_file: str, username: str = "anonymous", password: str = "anonymous@example.com", port: int = 21, timeout: int = 10) -> dict:
    """
    Download a file from FTP server.
    
    Args:
        ip (str): Target IP address
        remote_file (str): Path to the remote file to download
        local_file (str): Local path where to save the file
        username (str): FTP username (default: "anonymous")
        password (str): FTP password (default: "anonymous@example.com")
        port (int): FTP port (default: 21)
        timeout (int): Connection timeout in seconds (default: 10)
    
    Returns:
        dict: Contains success status, download details, and file information
    """
    try:
        # Create FTP connection
        ftp = FTP()
        ftp.set_debuglevel(0)
        
        # Set timeout and connect
        ftp.connect(ip, port, timeout)
        
        # Login
        ftp.login(username, password)
        
        # Get file size
        try:
            file_size = ftp.size(remote_file)
        except:
            file_size = "unknown"
        
        # Create local directory if needed
        local_dir = os.path.dirname(local_file)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir)
        
        # Download the file
        with open(local_file, 'wb') as f:
            ftp.retrbinary(f'RETR {remote_file}', f.write)
        
        # Verify download
        local_size = os.path.getsize(local_file) if os.path.exists(local_file) else 0
        
        ftp.quit()
        
        return {
            "success": True,
            "message": f"SUCCESS: Downloaded {remote_file} to {local_file}",
            "ip": ip,
            "port": port,
            "username": username,
            "remote_file": remote_file,
            "local_file": local_file,
            "remote_size": file_size,
            "local_size": local_size,
            "download_verified": local_size > 0
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if "550" in error_msg:
            return {
                "success": False,
                "message": f"File not found or access denied: {remote_file}",
                "ip": ip,
                "port": port,
                "username": username,
                "remote_file": remote_file,
                "error": "file_not_found_or_denied"
            }
        elif "530" in error_msg or "login" in error_msg:
            return {
                "success": False,
                "message": f"FTP login failed for {username} on {ip}:{port}",
                "ip": ip,
                "port": port,
                "username": username,
                "error": "login_failed"
            }
        else:
            return {
                "success": False,
                "message": f"Error downloading file: {str(e)}",
                "ip": ip,
                "port": port,
                "username": username,
                "remote_file": remote_file,
                "error": str(e)
            }

@mcp.tool()
def ftp_change_directory(ip: str, directory: str, username: str = "anonymous", password: str = "anonymous@example.com", port: int = 21, timeout: int = 10) -> dict:
    """
    Change directory on FTP server and list contents of the new directory.
    
    Args:
        ip (str): Target IP address
        directory (str): Directory path to change to (use ".." for parent, "/" for root)
        username (str): FTP username (default: "anonymous")
        password (str): FTP password (default: "anonymous@example.com")
        port (int): FTP port (default: 21)
        timeout (int): Connection timeout in seconds (default: 10)
    
    Returns:
        dict: Contains success status, new directory path, and directory listing
    """
    try:
        # Create FTP connection
        ftp = FTP()
        ftp.set_debuglevel(0)
        
        # Set timeout and connect
        ftp.connect(ip, port, timeout)
        
        # Login
        ftp.login(username, password)
        
        # Get current directory before change
        try:
            old_dir = ftp.pwd()
        except:
            old_dir = "unknown"
        
        # Change directory
        ftp.cwd(directory)
        
        # Get new current directory
        try:
            new_dir = ftp.pwd()
        except:
            new_dir = directory
        
        # List contents of new directory
        files_and_dirs = []
        detailed_listing = []
        
        try:
            # Get simple file list
            file_list = ftp.nlst()
            
            # Get detailed directory listing
            detailed_lines = []
            ftp.retrlines('LIST', detailed_lines.append)
            
            # Parse detailed listing
            for line in detailed_lines:
                parts = line.split()
                if len(parts) >= 9:
                    permissions = parts[0]
                    size = parts[4] if len(parts) > 4 else "unknown"
                    name = " ".join(parts[8:])
                    
                    item_type = "directory" if permissions.startswith('d') else "file"
                    
                    detailed_listing.append({
                        "name": name,
                        "type": item_type,
                        "permissions": permissions,
                        "size": size,
                        "raw_line": line
                    })
            
            files_and_dirs = file_list if file_list else [item["name"] for item in detailed_listing]
            
        except Exception as list_error:
            files_and_dirs = []
            detailed_listing = []
            list_error_msg = str(list_error)
        else:
            list_error_msg = None
        
        ftp.quit()
        
        return {
            "success": True,
            "message": f"SUCCESS: Changed directory to {new_dir}",
            "ip": ip,
            "port": port,
            "username": username,
            "old_directory": old_dir,
            "new_directory": new_dir,
            "requested_directory": directory,
            "files_and_directories": files_and_dirs,
            "detailed_listing": detailed_listing,
            "total_items": len(detailed_listing),
            "directories": [item for item in detailed_listing if item["type"] == "directory"],
            "files": [item for item in detailed_listing if item["type"] == "file"],
            "list_error": list_error_msg
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        if "550" in error_msg:
            return {
                "success": False,
                "message": f"Directory not found or access denied: {directory}",
                "ip": ip,
                "port": port,
                "username": username,
                "requested_directory": directory,
                "error": "directory_not_found_or_denied"
            }
        elif "530" in error_msg or "login" in error_msg:
            return {
                "success": False,
                "message": f"FTP login failed for {username} on {ip}:{port}",
                "ip": ip,
                "port": port,
                "username": username,
                "error": "login_failed"
            }
        else:
            return {
                "success": False,
                "message": f"Error changing directory: {str(e)}",
                "ip": ip,
                "port": port,
                "username": username,
                "requested_directory": directory,
                "error": str(e)
            }

@mcp.tool()
def ssh_connect_password(ip: str, username: str, password: str, port: int = 22, timeout: int = 10) -> dict:
    """
    Connect to SSH server using username and password authentication.
    
    Args:
        ip (str): Target IP address
        username (str): SSH username
        password (str): SSH password
        port (int): SSH port (default: 22)
        timeout (int): Connection timeout in seconds (default: 10)
    
    Returns:
        dict: Contains success status, connection details, and system information
    """
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect with password authentication
        ssh.connect(ip, port=port, username=username, password=password, timeout=timeout)
        
        # Get system information
        stdin, stdout, stderr = ssh.exec_command('uname -a && whoami && pwd')
        system_info = stdout.read().decode().strip()
        
        # Get directory listing
        stdin, stdout, stderr = ssh.exec_command('ls -la')
        directory_listing = stdout.read().decode().strip()
        
        # Close connection
        ssh.close()
        
        return {
            "success": True,
            "message": f"SUCCESS: SSH password authentication successful for {username}@{ip}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": "password",
            "system_info": system_info,
            "directory_listing": directory_listing,
            "connection_verified": True
        }
        
    except paramiko.AuthenticationException:
        return {
            "success": False,
            "message": f"SSH authentication failed for {username}@{ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": "password",
            "error": "authentication_failed"
        }
    except socket.timeout:
        return {
            "success": False,
            "message": f"SSH connection timeout to {ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "error": "timeout"
        }
    except ConnectionRefusedError:
        return {
            "success": False,
            "message": f"SSH connection refused to {ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "error": "connection_refused"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"SSH connection error: {str(e)}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": "password",
            "error": str(e)
        }

@mcp.tool()
def ssh_connect_key(ip: str, username: str, private_key: str, key_password: str = "", port: int = 22, timeout: int = 10) -> dict:
    """
    Connect to SSH server using private key authentication.
    
    Args:
        ip (str): Target IP address
        username (str): SSH username
        private_key (str): Private key content (PEM format) or path to private key file
        key_password (str): Private key passphrase if encrypted (default: "")
        port (int): SSH port (default: 22)
        timeout (int): Connection timeout in seconds (default: 10)
    
    Returns:
        dict: Contains success status, connection details, and system information
    """
    temp_key_file = None
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Handle private key - check if it's a file path or key content
        if os.path.isfile(private_key):
            # It's a file path
            key_file = private_key
        else:
            # It's key content, create temporary file
            temp_key_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem')
            temp_key_file.write(private_key)
            temp_key_file.close()
            key_file = temp_key_file.name
        
        # Load the private key
        try:
            pkey = paramiko.RSAKey.from_private_key_file(key_file, password=key_password if key_password else None)
        except paramiko.ssh_exception.SSHException:
            try:
                pkey = paramiko.Ed25519Key.from_private_key_file(key_file, password=key_password if key_password else None)
            except paramiko.ssh_exception.SSHException:
                try:
                    pkey = paramiko.ECDSAKey.from_private_key_file(key_file, password=key_password if key_password else None)
                except paramiko.ssh_exception.SSHException:
                    pkey = paramiko.DSSKey.from_private_key_file(key_file, password=key_password if key_password else None)
        
        # Connect with key authentication
        ssh.connect(ip, port=port, username=username, pkey=pkey, timeout=timeout)
        
        # Get system information
        stdin, stdout, stderr = ssh.exec_command('uname -a && whoami && pwd')
        system_info = stdout.read().decode().strip()
        
        # Get directory listing
        stdin, stdout, stderr = ssh.exec_command('ls -la')
        directory_listing = stdout.read().decode().strip()
        
        # Get key fingerprint
        key_fingerprint = pkey.get_fingerprint().hex()
        
        # Close connection
        ssh.close()
        
        return {
            "success": True,
            "message": f"SUCCESS: SSH key authentication successful for {username}@{ip}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": "private_key",
            "key_fingerprint": key_fingerprint,
            "system_info": system_info,
            "directory_listing": directory_listing,
            "connection_verified": True
        }
        
    except paramiko.AuthenticationException:
        return {
            "success": False,
            "message": f"SSH key authentication failed for {username}@{ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": "private_key",
            "error": "authentication_failed"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"SSH key connection error: {str(e)}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": "private_key",
            "error": str(e)
        }
    finally:
        # Clean up temporary key file
        if temp_key_file and os.path.exists(temp_key_file.name):
            os.unlink(temp_key_file.name)

@mcp.tool()
def ssh_execute_command(ip: str, command: str, username: str, password: str = "", private_key: str = "", key_password: str = "", port: int = 22, timeout: int = 10) -> dict:
    """
    Execute a command on remote SSH server.
    
    Args:
        ip (str): Target IP address
        command (str): Command to execute on remote server
        username (str): SSH username
        password (str): SSH password (use if not using private key)
        private_key (str): Private key content or path (use if not using password)
        key_password (str): Private key passphrase if encrypted
        port (int): SSH port (default: 22)
        timeout (int): Connection timeout in seconds (default: 10)
    
    Returns:
        dict: Contains command output, success status, and execution details
    """
    temp_key_file = None
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Determine authentication method
        if private_key:
            # Use key authentication
            if os.path.isfile(private_key):
                key_file = private_key
            else:
                temp_key_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem')
                temp_key_file.write(private_key)
                temp_key_file.close()
                key_file = temp_key_file.name
            
            # Load the private key
            try:
                pkey = paramiko.RSAKey.from_private_key_file(key_file, password=key_password if key_password else None)
            except paramiko.ssh_exception.SSHException:
                try:
                    pkey = paramiko.Ed25519Key.from_private_key_file(key_file, password=key_password if key_password else None)
                except paramiko.ssh_exception.SSHException:
                    try:
                        pkey = paramiko.ECDSAKey.from_private_key_file(key_file, password=key_password if key_password else None)
                    except paramiko.ssh_exception.SSHException:
                        pkey = paramiko.DSSKey.from_private_key_file(key_file, password=key_password if key_password else None)
            
            ssh.connect(ip, port=port, username=username, pkey=pkey, timeout=timeout)
            auth_method = "private_key"
        else:
            # Use password authentication
            ssh.connect(ip, port=port, username=username, password=password, timeout=timeout)
            auth_method = "password"
        
        # Execute command
        stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
        
        # Get output
        stdout_output = stdout.read().decode().strip()
        stderr_output = stderr.read().decode().strip()
        exit_status = stdout.channel.recv_exit_status()
        
        # Close connection
        ssh.close()
        
        return {
            "success": True,
            "message": f"SUCCESS: Command executed on {username}@{ip}",
            "ip": ip,
            "port": port,
            "username": username,
            "auth_type": auth_method,
            "command": command,
            "stdout": stdout_output,
            "stderr": stderr_output,
            "exit_status": exit_status,
            "command_successful": exit_status == 0
        }
        
    except paramiko.AuthenticationException:
        return {
            "success": False,
            "message": f"SSH authentication failed for {username}@{ip}:{port}",
            "ip": ip,
            "port": port,
            "username": username,
            "command": command,
            "error": "authentication_failed"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"SSH command execution error: {str(e)}",
            "ip": ip,
            "port": port,
            "username": username,
            "command": command,
            "error": str(e)
        }
    finally:
        # Clean up temporary key file
        if temp_key_file and os.path.exists(temp_key_file.name):
            os.unlink(temp_key_file.name)

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

@mcp.tool()
def enum4linux_scan(ip: str, username: str = "", password: str = "", domain: str = "", all_enum: bool = True, timeout: int = 120) -> dict:
    """
    Enumerate SMB shares and information using enum4linux.
    
    Args:
        ip (str): Target IP address
        username (str): SMB username for authenticated enumeration (optional)
        password (str): SMB password for authenticated enumeration (optional)
        domain (str): SMB domain name (optional)
        all_enum (bool): Use -a flag for all enumeration (default: True)
        timeout (int): Command timeout in seconds (default: 120)
    
    Returns:
        dict: Contains enum4linux output, shares found, and enumeration results
    """
    try:
        # Build enum4linux command
        command = ["enum4linux"]
        
        if all_enum:
            command.append("-a")
        else:
            # Add individual enumeration flags if not using -a
            command.extend(["-U", "-S", "-G", "-P", "-o"])
        
        # Add credentials if provided
        if username and password:
            command.extend(["-u", username, "-p", password])
            auth_type = "authenticated"
            if domain:
                command.extend(["-d", domain])
        else:
            auth_type = "anonymous"
        
        # Add target IP
        command.append(ip)
        
        # Execute command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Parse output for key information
        output = result.stdout
        shares = []
        users = []
        groups = []
        os_info = ""
        
        # Extract shares
        if "Sharename" in output:
            lines = output.split('\n')
            in_shares_section = False
            for line in lines:
                if "Sharename" in line and "Type" in line:
                    in_shares_section = True
                    continue
                elif in_shares_section and line.strip():
                    if line.startswith('\t') or '|' in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            share_name = parts[0].strip('|').strip()
                            share_type = parts[1].strip('|').strip() if len(parts) > 1 else "unknown"
                            if share_name and share_name != "Sharename":
                                shares.append({
                                    "name": share_name,
                                    "type": share_type,
                                    "comment": " ".join(parts[2:]).strip('|').strip() if len(parts) > 2 else ""
                                })
                    elif not line.strip().startswith('|') and not line.strip().startswith('-'):
                        in_shares_section = False
        
        # Extract users
        if "Users on" in output:
            lines = output.split('\n')
            for line in lines:
                if "Users on" in line or line.strip().startswith("user:"):
                    if "user:[" in line:
                        user_match = line.split("user:[")[1].split("]")[0] if "]" in line else ""
                        if user_match and user_match not in users:
                            users.append(user_match)
        
        # Extract OS information
        for line in output.split('\n'):
            if "OS information on" in line or "Target OS:" in line:
                os_info = line.strip()
                break
        
        # Determine success
        success = result.returncode == 0 or shares or users
        
        if success:
            message = f"SUCCESS: enum4linux scan completed for {ip}"
            if shares:
                message += f" - Found {len(shares)} shares"
            if users:
                message += f" - Found {len(users)} users"
        else:
            message = f"enum4linux scan completed with issues for {ip}"
        
        return {
            "success": success,
            "message": message,
            "ip": ip,
            "auth_type": auth_type,
            "username": username if username else "anonymous",
            "domain": domain,
            "command": " ".join(command),
            "raw_output": output,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "shares": shares,
            "users": users,
            "groups": groups,
            "os_info": os_info,
            "shares_count": len(shares),
            "users_count": len(users),
            "enumeration_successful": len(shares) > 0 or len(users) > 0
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": f"enum4linux scan timed out after {timeout} seconds for {ip}",
            "ip": ip,
            "auth_type": auth_type if 'auth_type' in locals() else "unknown",
            "error": "timeout",
            "command": " ".join(command) if 'command' in locals() else "enum4linux"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": "enum4linux tool not found - please install enum4linux package",
            "ip": ip,
            "error": "tool_not_found",
            "install_hint": "sudo apt-get install enum4linux-ng"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error running enum4linux scan: {str(e)}",
            "ip": ip,
            "error": str(e),
            "command": " ".join(command) if 'command' in locals() else "enum4linux"
        }

if __name__ == "__main__":
    # Run the MCP server with stdio transport
    mcp.run(transport="stdio")