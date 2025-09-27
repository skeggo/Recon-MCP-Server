# Reconnaissance MCP Server

A modular MCP (Model Context Protocol) server built with FastMCP for running reconnaissance and footprinting tasks in a secure environment.

## 🚀 Features

- **MCP-compliant server** using FastMCP framework
- **Single unified interface** (`run_tool`) for executing reconnaissance commands
- **Pre-installed reconnaissance tools** including nmap, whois, dnsutils, and more
- **Portable and reusable** across different environments
- **Security-focused** with timeouts and proper error handling

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Linux/macOS/Windows with WSL2

### Python Dependencies
```
fastmcp>=2.0.0
```

## 🛠️ Installation & Setup

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Recon-MCP-Server
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t recon-mcp .
   ```

3. **Run the container:**
   ```bash
   docker run -i recon-mcp
   ```

### Option 2: Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo-url>
   cd Recon-MCP-Server
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python server.py
   ```

## ⚙️ Configuration

### MCP Client Configuration

To use this server with Claude Desktop or other MCP clients, add the following to your MCP configuration:

#### For Claude Desktop (Linux/macOS):
Location: `~/.config/claude/mcp.json`

```json
{
  "servers": {
    "recon-server": {
      "command": "python",
      "args": ["/path/to/your/Recon-MCP-Server/server.py"],
      "env": {}
    }
  }
}
```

#### For Claude Desktop (Windows):
Location: `%APPDATA%\Claude\mcp.json`

```json
{
  "servers": {
    "recon-server": {
      "command": "python",
      "args": ["C:\\path\\to\\your\Recon-MCP-Server\\server.py"],
      "env": {}
    }
  }
}
```

### Environment Variables

You can customize the server behavior with environment variables:

- `MCP_SERVER_NAME`: Server name (default: "recon-server")
- `TOOL_TIMEOUT`: Command timeout in seconds (default: 300)

## 🔧 Usage

### Available Tool

The server exposes a single MCP tool:

#### `run_tool`
Executes reconnaissance tools with specified arguments.

**Parameters:**
- `tool` (string): The command to run (e.g., 'nmap', 'dig', 'whois')
- `args` (list of strings): Arguments for the tool

**Returns:**
```json
{
  "stdout": "command output",
  "stderr": "error output if any",
  "returncode": 0,
  "command": "full command that was executed"
}
```

### Example Usage

#### Network Scanning
```json
{
  "tool": "nmap",
  "args": ["-sn", "192.168.1.0/24"]
}
```

#### DNS Lookup
```json
{
  "tool": "dig",
  "args": ["example.com", "A"]
}
```

#### Domain Information
```json
{
  "tool": "whois",
  "args": ["example.com"]
}
```

#### Web Technology Detection
```json
{
  "tool": "whatweb",
  "args": ["https://example.com"]
}
```

## ⚠️ Disclaimer

**IMPORTANT: This tool is intended for authorized security professionals and researchers only.**

- This software is provided for educational and authorized penetration testing purposes only
- Users are responsible for compliance with all applicable laws and regulations
- Unauthorized access to computer networks, systems, or data is illegal and unethical
- Always ensure you have explicit written permission before conducting any reconnaissance activities
- The authors and contributors are not responsible for any misuse of this tool
- Use of this tool may trigger security alerts or be detected by monitoring systems
- Some reconnaissance techniques may be considered aggressive and could impact target systems
- Users assume all legal and ethical responsibility for their actions

**By using this tool, you acknowledge that you understand these restrictions and agree to use it only for lawful purposes.**
